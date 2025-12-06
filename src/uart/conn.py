# conn.py
# 串口连接管理模块
#
# @author n1ghts4kura
# @date 25-12-6
#

import os
import time
import queue
import threading
import serial as s

from src import config
from src import logger

# 串口连接对象
serial_conn: s.Serial | None = None
# 串口连接锁
# serial_access_lock = threading.Lock()

# 接收队列
rx_queue: queue.Queue[str] = queue.Queue() 
# 接收线程
_rx_thread: threading.Thread | None = None
# 接收线程运行标志
_rx_stop: threading.Event = threading.Event()


def open_serial() -> bool:
    """
    打开串口对象

    Returns:
        bool: 是否成功打开
    """

    os.system(f"sudo chmod 777 {config.SERIAL_PORT}") # 修改串口权限

    global serial_conn
    try:

        serial_conn = s.Serial(
            port = config.SERIAL_PORT,
            baudrate = config.SERIAL_BAUDRATE,
            timeout = config.SERIAL_TIMEOUT,
            bytesize = config.SERIAL_BYTESIZE,
            parity = config.SERIAL_PARITY,
            stopbits = config.SERIAL_STOPBITS
        )

        serial_conn.open()

        if serial_conn.is_open:
            return True

    except Exception as e:
        serial_conn = None
        logger.error(f"打开串口 出现异常: {e}")

    finally:
        return False


def writeline(data: str) -> bool:
    """
    向串口写入字符串

    Args:
        data (str): 要写入的字符串
    Returns:
        bool: 是否写入成功
    """

    global serial_conn
    if serial_conn is None or not serial_conn.is_open:
        return False
    
    try:
        serial_conn.write(f"{data};{config.SERIAL_EOL}".encode("utf-8"))
        serial_conn.flush() # 刷新缓冲区确保写入
        return True
    except Exception as e:
        logger.error(f"写入串口 出现异常: {e}")
        return False


def _rx_worker() -> None:
    """
    接收线程 循环函数
    """

    global serial_conn, rx_queue

    # 等待连接成功
    while not serial_conn or not serial_conn.is_open:
        time.sleep(0.5)
    
    while not _rx_stop.is_set():
        try:
            # 获取当前缓冲区有多少字节
            n = serial_conn.in_waiting
            if n <= 0:
                continue
        
            # 读取出来
            data = serial_conn.read(n).decode("utf-8")
            # 按行分割
            lines = data.split(config.SERIAL_EOL)
            # 将处理后的有效数据放入队列
            for line in lines:
                line = line.strip()
                if line:
                    rx_queue.put(line)

        except Exception as e:
            logger.error(f"接收串口数据 出现异常: {e}")

        finally:
            time.sleep(config.SERIAL_RX_READ_DELAY)


def start_rx_thread() -> None:
    """
    启动串口接收线程
    """

    global _rx_thread, _rx_stop

    if _rx_thread and _rx_thread.is_alive():
        return
    
    _rx_stop.clear()
    _rx_thread = threading.Thread(target=_rx_worker, daemon=True)
    _rx_thread.start()


def stop_rx_thread() -> None:
    """
    停止串口接收线程
    """

    global _rx_thread, _rx_stop

    if not _rx_thread:
        return
    
    _rx_stop.set()
    _rx_thread.join()
    _rx_thread = None


def readline() -> str | None:
    """
    从串口读取数据 (非阻塞)

    Returns:
        str: 获取到的数据
        None: 无数据可读
    """

    global rx_queue

    try:
        data = rx_queue.get_nowait()
        return data
    except queue.Empty:
        return None


def readline_blocking(timeout: float | None = None) -> str | None:
    """
    从串口读取数据 (阻塞)

    Args:
        timeout (float | None): 超时时间，单位秒，None表示无限等待

    Returns:
        str: 获取到的数据
        None: 超时无数据可读
    """

    global rx_queue

    try:
        data = rx_queue.get(timeout=timeout)
        return data
    except queue.Empty:
        return None


def readall() -> list[str]:
    """
    读取串口接收队列中所有数据

    Returns:
        list[str]: 获取到的数据列表
    """

    global rx_queue

    return list(rx_queue.queue) # 直接访问队列底层


def readall_blocking(delay: float) -> list[str]:
    """
    阻塞读取串口接收队列中所有数据

    Args:
        delay (float): 等待时间，单位秒
    Returns:
        list[str]: 获取到的数据列表
    """

    global rx_queue

    time.sleep(delay)
    return list(rx_queue.queue) # 直接访问队列底层


def clear_rx_queue() -> None:
    """
    清除串口接收队列中的所有数据
    """

    global rx_queue

    with rx_queue.mutex:
        rx_queue.queue.clear()


def handshake_serial() -> bool:
    """
    检测串口连接是否可用

    Returns:
        bool: 是否连接成功
    """

    global serial_conn
    if serial_conn is None or not serial_conn.is_open:
        return False
    
    writeline("quit;") # 先退出当前可能的会话
    time.sleep(0.1)
    writeline("command;") # 启动会话

    result = readall_blocking(5.0)
    if len(result) == 0:
        logger.error("启动会话5秒内无应答")
        return False

    # 检查应答内容 如果找不到"ok;"则表示失败
    if "ok;" in result:
        logger.error(f"启动会话应答异常 应答内容[{result}]")
        return False
    
    writeline("quit;") # 退出会话 **消除副作用**
    time.sleep(0.1)
    
    return True


__all__ = [
    "open_serial",
    "writeline",
    "readline",
    "readline_blocking",
    "readall",
    "readall_blocking",
    "handshake_serial",
    "start_rx_thread",
    "stop_rx_thread",

    "rx_queue",
]