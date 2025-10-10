#
# conn.py
#
# @author n1ghts4kura
# @date 2025/9/28
#

import os
import serial as s
from threading import Lock, Thread, Event
from time import monotonic, sleep
from queue import Queue, Empty

import config
import logger as LOG

# uart连接配置
serial_conn: s.Serial | None = None
serial_conn_lock = Lock()

_rx_buf = bytearray() # 接收缓冲区
_rx_last_activity: float = 0.0
_RX_IDLE_SEC = 0.1  # 空闲超过该时间且缓冲非空，则按一帧返回
_RX_THREAD_IDLE_SEC_DEFAULT = 0.05

# 后台接收线程/队列
_rx_thread: Thread | None = None
_rx_stop: Event | None = None
_rx_queue: Queue[str] | None = None
# 指令队列（以分号;分隔）
_cmd_queue: Queue[str] | None = None
_cmd_buffer: str = ""


def open_serial() -> bool:
    """
    打开 UART 连接，启动后台接收线程，并验证下位机响应。

    Returns:
        (bool) 是否成功打开并收到下位机 ok 确认
    """

    # **ATTENTION*
    # 在使用usb-to-ttl工具前
    # YOU SHOULD KNOW:
    # `lsusb` 是用来检测usb接口上接了什么东西的
    # `ls /dev/tty*` 是用来检测串口端口映射情况的
    # 请在使用前执行以下步骤
    # 1. 补药接上usb-to-ttl转接器 使用`lsusb` `ls /dev/tty*`指令
    # 2. 接上转接器 再使用上述指令
    # 重复这两个步骤，直到你知道这个转接口对应的端口到底是/dev/ttyACM0 还是/dev/ttyS0 还是/dev/ttyUSB0 还是......
    # 然后根据这一台树莓派使用的转接口（每个转接口对应的端口大概率不一样！！）
    # 设置_device_address变量
    
    _device_address = config.SERIAL_PORT
    os.system(f"sudo chmod 777 {_device_address}") # 设置设备权限

    global serial_conn
    try:
        serial_conn = s.Serial(
            port=_device_address,
            baudrate=115200,         # 波特率
            bytesize=s.EIGHTBITS,    # 数据位
            parity=s.PARITY_NONE,    # 校验位
            stopbits=s.STOPBITS_ONE, # 停止位
            timeout=10,
        )
        
        if not serial_conn.is_open:
            LOG.error("串口打开失败")
            return False
        
        # 启动后台接收线程
        LOG.info("启动串口后台接收线程...")
        if not start_serial_worker():
            LOG.error("后台接收线程启动失败")
            return False
        
        sleep(0.5)  # 等待线程启动
        
        # 清空接收缓冲区，避免旧数据干扰
        while get_serial_command_nowait():
            pass
        
        # 发送测试命令，验证下位机响应
        LOG.info("发送测试命令，验证下位机连接...")
        write_serial("command;")  # 使用 version 命令测试连接
        
        # 等待并验证下位机响应
        max_wait = 5  # 最多等待 3 秒
        start_time = monotonic()
        success = False
        
        while monotonic() - start_time < max_wait:
            response = get_serial_command_nowait()
            if response:
                LOG.debug(f"收到响应: {response.strip()}")
                # 检查是否包含版本信息或 ok（任意响应都说明连接成功）
                if response.strip():
                    success = True
                    LOG.info(f"✅ 下位机连接确认成功: {response.strip()}")
                    break
            sleep(0.1)
        
        if not success:
            LOG.error("❌ 未收到下位机响应！请检查：")
            LOG.error("   1. 串口连接是否正确")
            LOG.error("   2. 下位机是否上电")
            LOG.error("   3. 波特率是否匹配(115200)")
            return False
        
        return True
        
    except Exception as e:
        LOG.error(f"打开串口时发生异常: {e}")
        return False


def read_serial_line() -> str:
    """
    阻塞读取一行串口数据（去除首尾空白）。

    Returns:
        (str) 读取到的数据行，若连接未打开则返回空字符串
    """

    if serial_conn is None or not serial_conn.is_open:
        LOG.debug("Serial connection is not open.")
        return ""

    global serial_conn_lock

    with serial_conn_lock:
        data = ""
        try:
            data = serial_conn.readline().decode('utf-8').strip()
        except s.SerialException as e:
            LOG.exception("Serial read error: %s", e)
        except UnicodeDecodeError as e:
            LOG.exception("Unicode decode error: %s", e)

    return data


def read_serial_nonblock() -> str:
    """
    非阻塞读取一行串口数据；若无完整行则返回空字符串。

    Returns:
        (str) 读取到的数据行，若无数据则返回空字符串
    """

    global serial_conn, serial_conn_lock, _rx_buf, _rx_last_activity
    if serial_conn is None or not serial_conn.is_open:
        return ""

    with serial_conn_lock:
        try:
            n = serial_conn.in_waiting
            if n and n > 0:
                _rx_buf.extend(serial_conn.read(n))
                _rx_last_activity = monotonic()
            # 查找 CR 或 LF 作为行结束
            lf = _rx_buf.find(b"\n")
            cr = _rx_buf.find(b"\r")
            idxs = [i for i in (lf, cr) if i != -1]
            if idxs:
                idx = min(idxs)
                line_bytes = _rx_buf[: idx + 1]
                del _rx_buf[: idx + 1]
                # 去掉 CR/LF
                line_bytes = line_bytes.rstrip(b"\r\n")
                try:
                    return line_bytes.decode("utf-8", errors="replace")
                except Exception:
                    return line_bytes.decode("latin1", errors="replace")
            # 若无行结束，但缓冲有内容且已空闲一段时间，则把缓冲当作一帧返回
            if _rx_buf and _rx_last_activity and (monotonic() - _rx_last_activity) > _RX_IDLE_SEC:
                line_bytes = bytes(_rx_buf)
                _rx_buf.clear()
                try:
                    return line_bytes.decode("utf-8", errors="replace")
                except Exception:
                    return line_bytes.decode("latin1", errors="replace")
        except s.SerialException as e:
            LOG.exception("Serial non-blocking read error: %s", e)
        except Exception as e:
            LOG.exception("Unexpected error in read_serial_nonblock: %s", e)
    return ""


def _enqueue_received_text(text: str) -> None:
    """
    将收到的文本放入行队列与指令队列。
    """

    global _rx_queue, _cmd_queue, _cmd_buffer
    if _rx_queue is not None:
        _rx_queue.put(text)
    if _cmd_queue is None:
        return

    _cmd_buffer += text
    while True:
        idx = _cmd_buffer.find(";")
        if idx == -1:
            break
        command = _cmd_buffer[:(idx + 1)].strip()
        _cmd_buffer = _cmd_buffer[idx + 1 :]
        if command:
            _cmd_queue.put(command)


def write_serial(data: str) -> bool:
    """
    向UART发送数据

    Args:
        data (str): 要发送的数据
    Returns:
        bool: 是否成功发送
    """

    if serial_conn is None or not serial_conn.is_open:
        LOG.debug("Serial connection is not open.")
        return False

    with serial_conn_lock:
        try:
            serial_conn.write(data.encode('utf-8'))
            # 立即刷新，确保数据立刻下发
            try:
                serial_conn.flush()
            except Exception:
                pass
            return True

        except s.SerialException as e:
            LOG.exception("Serial write error: %s", e)
            return False


def close_serial() -> None:
    """
    关闭UART连接
    """

    global serial_conn, _rx_stop, _rx_thread, _rx_queue, _cmd_queue, _cmd_buffer
    # 先停止后台读取线程
    if _rx_stop is not None:
        try:
            _rx_stop.set()
        except Exception:
            pass

    if _rx_thread is not None and _rx_thread.is_alive():
        try:
            _rx_thread.join(timeout=1.0)
        except Exception:
            pass

    _rx_stop = None
    _rx_thread = None
    _rx_queue = None
    _cmd_queue = None
    _cmd_buffer = ""
    if serial_conn is not None:
        try:
            if serial_conn.is_open:
                serial_conn.close()
        except s.SerialException as e:
            LOG.exception("Serial close error: %s", e)
        finally:
            serial_conn = None


def _rx_worker_loop(idle_timeout_sec: float):
    """
    后台读取线程主循环，将解析后的文本行推入内部队列。
    """

    global serial_conn, _rx_buf, _rx_last_activity, _rx_stop, _rx_queue
    if serial_conn is None or not serial_conn.is_open:
        return
    _rx_last_activity = monotonic()

    while _rx_stop is not None and not _rx_stop.is_set():
        try:
            n = serial_conn.in_waiting if serial_conn is not None else 0
            if n and n > 0:
                data = serial_conn.read(n)
                if data:
                    _rx_buf.extend(data)
                    _rx_last_activity = monotonic()
                # 处理行结束（CR/LF）
                while True:
                    lf = _rx_buf.find(b"\n")
                    cr = _rx_buf.find(b"\r")
                    idxs = [i for i in (lf, cr) if i != -1]
                    if not idxs:
                        break
                    idx = min(idxs)
                    line_bytes = _rx_buf[: idx + 1]
                    del _rx_buf[: idx + 1]
                    line = line_bytes.rstrip(b"\r\n").decode("utf-8", errors="replace")
                    _enqueue_received_text(line)
            else:
                # 空闲超时：将缓冲作为一帧输出
                if _rx_buf and _rx_last_activity and (monotonic() - _rx_last_activity) > idle_timeout_sec:
                    line = bytes(_rx_buf).decode("utf-8", errors="replace")
                    _rx_buf.clear()
                    _enqueue_received_text(line)
                sleep(0.002)
        except Exception as e:
            # 不中断循环，避免高频报错导致线程退出
            LOG.debug(f"RX worker error: {e}")
            sleep(0.01)


def start_serial_worker(idle_timeout_sec: float = _RX_THREAD_IDLE_SEC_DEFAULT) -> bool:
    """
    启动后台读取线程，将解析后的文本行推入内部队列。重复调用是安全的。

    Returns:
        (bool) 是否成功启动
    """

    global _rx_thread, _rx_stop, _rx_queue, _cmd_queue, _cmd_buffer
    if serial_conn is None or not serial_conn.is_open:
        return False
    if _rx_thread is not None and _rx_thread.is_alive():
        return True

    _rx_stop = Event()
    _rx_queue = Queue(maxsize=0)
    _cmd_queue = Queue(maxsize=0)
    _cmd_buffer = ""
    _rx_thread = Thread(target=_rx_worker_loop, args=(idle_timeout_sec,), daemon=True)
    _rx_thread.start()
    return True


def get_serial_line_nowait() -> str:
    """
    从内部队列无阻塞取一行。

    Returns:
        (str) 取到的行，若无则返回空字符串
    """

    global _rx_queue
    if _rx_queue is None:
        return ""
    try:
        return _rx_queue.get_nowait()
    except Empty:
        return ""


def get_serial_command_nowait() -> str:
    """
    从指令队列无阻塞取一条分号分隔的指令。
    
    Returns:
        (str) 取到的指令，若无则返回空字符串
    """
    global _cmd_queue
    if _cmd_queue is None:
        return ""
    try:
        return _cmd_queue.get_nowait()
    except Empty:
        return ""

__all__ = [
    "open_serial",
    "read_serial_line",
    "read_serial_nonblock",
    "write_serial",
    "close_serial",
    "start_serial_worker",
    "get_serial_line_nowait",
    "get_serial_command_nowait",
]
