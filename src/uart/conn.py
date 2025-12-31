# conn.py
# 串口连接管理模块
#
# @author n1ghts4kura
# @date 25-12-31
#


from queue import Queue
from typing import Optional
from threading import Thread, Event, Lock
import time
import serial as s

from src import config
from src import logger


# 串口连接
serial_conn = s.Serial(
    baudrate = config.SERIAL_BAUDRATE,
    bytesize = config.SERIAL_BYTESIZE,
    parity   = config.SERIAL_PARITY,
    stopbits = config.SERIAL_STOPBITS,
    timeout  = config.SERIAL_TIMEOUT
)
serial_conn.port = config.SERIAL_PORT
# 串口锁：保护读写/重连期间的串口访问
serial_lock = Lock()
# 串口状态
serial_connected = False

# 信息队列
rx_queue = Queue()
# 信息接收线程
rx_thread: Optional[Thread] = None
# 信息接收线程停止事件
rx_thread_stop_event = Event()
# 接收缓冲区（未完整的行片段）
_rx_buffer = ""

# 写队列
tx_queue = Queue()
# 写线程
tx_thread: Optional[Thread] = None
# 写线程停止事件
tx_thread_stop_event = Event()


_REOPEN_DELAY = 2 # 串口重连延迟 秒
def _open_serial_blocking() -> None:
    """
    重连串口 阻塞
    """

    global serial_conn, serial_connected

    while True:
        try:
            serial_connected = False
            serial_conn.close()
            serial_conn.open()
            logger.info(f"串口已重连: {serial_conn.port}")
            serial_connected = True
            return

        except s.SerialException as e:
            logger.warning(f"串口重连失败: {e}")
            logger.info(f"{_REOPEN_DELAY}秒后重试...")
            time.sleep(_REOPEN_DELAY)
            serial_connected = False


def _rx_thread_worker() -> None:
    """
    信息接收线程：in_waiting 拉取数据，按 EOL 拆分入队；掉线时阻塞重连。
    """

    global serial_conn, rx_queue, rx_thread_stop_event, _rx_buffer, serial_connected

    logger.info("信息接收线程已启动")

    while not rx_thread_stop_event.is_set():

        if not serial_conn.is_open:
            logger.warning("串口连接已断开，正在重连...")
            _open_serial_blocking()
            _rx_buffer = ""  # 重连后清空残余片段
            continue
        
        try:
            # 若写线程持锁，暂缓读取，避免在写/重连时同时读
            if serial_lock.locked():
                time.sleep(config.SERIAL_RX_DELAY)
                continue

            waiting = serial_conn.in_waiting
            if waiting <= 0:
                time.sleep(config.SERIAL_RX_DELAY) # 无数据时短暂休眠
                continue

            raw = serial_conn.read(waiting)
            logger.debug(f"接收到一行原始数据: {raw}")
            try:
                decoded = raw.decode()
            except UnicodeDecodeError:
                decoded = raw.decode(errors="replace")

            _rx_buffer += decoded # 累积到缓冲区

            while True:
                idx = _rx_buffer.find(config.SERIAL_EOL)
                if idx == -1:
                    break
                line = _rx_buffer[:idx]
                _rx_buffer = _rx_buffer[idx + len(config.SERIAL_EOL):]
                if line:
                    rx_queue.put(line)
                    logger.debug(f"已将一行数据入队: {line}")
            logger.debug(f"当前接收缓冲区内容: {_rx_buffer}")

        except s.SerialException as e:
            logger.warning(f"串口读取失败: {e}")

        except Exception as e:
            logger.warning(f"串口接收异常: {e}")
            if "Errno 5" in str(e):
                logger.warning("检测到串口可能已断开，正在重连...")
                serial_conn.close()
                serial_connected = False
        
        finally:
            # 无论如何，短暂休眠以避免忙等待
            time.sleep(config.SERIAL_RX_DELAY)
        
    logger.info("信息接收线程已停止")


def _start_rx_thread() -> bool:
    """
    启动信息接收线程
    """

    global rx_thread, rx_thread_stop_event

    if rx_thread is not None and rx_thread.is_alive():
        logger.warning("信息接收线程已在运行，无法重复启动")
        return False

    rx_thread_stop_event.clear() # 清除停止事件
    rx_thread = Thread(target=_rx_thread_worker, daemon=True) # 守护线程
    rx_thread.start() # 启动线程
    return True


def _stop_rx_thread() -> bool:
    """
    停止信息接收线程 阻塞
    """

    global rx_thread, rx_thread_stop_event

    if rx_thread is None or not rx_thread.is_alive():
        logger.warning("信息接收线程未在运行，无法停止")
        return False

    rx_thread_stop_event.set() # 设置停止事件
    rx_thread.join() # 等待线程结束
    return True


def readline() -> str:
    """
    从接收队列读取一行数据 阻塞
    """

    data = rx_queue.get() # 阻塞等待数据
    logger.info(f"读取了一行数据: {data}")
    return data


def _tx_thread_worker() -> None:
    """
    信息发送线程：从写队列取数据并发送。
    """

    global serial_conn, tx_queue, tx_thread_stop_event, serial_connected

    logger.info("信息发送线程已启动")

    while not tx_thread_stop_event.is_set():

        # 这里不放置串口断开重连逻辑
        # 连不到就等 `rx_thread` 重连好了再发
        
        try:
            if serial_connected:
                line = tx_queue.get() # 阻塞等待数据
                with serial_lock:
                    serial_conn.write( f"{line}{config.SERIAL_EOL}".encode() )
                    serial_conn.flush()
                logger.debug(f"已发送一行数据: {line}")

        except s.SerialException as e:
            logger.warning(f"串口写入失败: {e}")

        except Exception as e:
            logger.warning(f"串口发送异常: {e}")
        
        finally:
            time.sleep(config.SERIAL_TX_DELAY) # 短暂休眠以避免忙等待
        
    logger.info("信息发送线程已停止")


def _start_tx_thread() -> bool:
    """
    启动信息发送线程
    """

    global tx_thread, tx_thread_stop_event

    if tx_thread is not None and tx_thread.is_alive():
        logger.warning("信息发送线程已在运行，无法重复启动")
        return False

    tx_thread_stop_event.clear() # 清除停止事件
    tx_thread = Thread(target=_tx_thread_worker, daemon=True) # 守护线程
    tx_thread.start() # 启动线程
    return True


def _stop_tx_thread() -> bool:
    """
    停止信息发送线程 阻塞
    """

    global tx_thread, tx_thread_stop_event

    if tx_thread is None or not tx_thread.is_alive():
        logger.warning("信息发送线程未在运行，无法停止")
        return False

    tx_thread_stop_event.set() # 设置停止事件
    tx_thread.join() # 等待线程结束
    return True


def writeline(line: str) -> None:
    """
    向发送队列写入一行数据

    Args:
        line (str): 要发送的行数据
    """

    global tx_queue

    tx_queue.put(line)
    logger.info(f"已将一行数据入发送队列: {line}")


def start_backend() -> None:
    """
    启动串口连接后台线程
    """

    _start_rx_thread()
    _start_tx_thread()
    logger.info("串口连接后台线程已启动")


def stop_backend() -> None:
    """
    停止串口连接后台线程 阻塞
    """

    _stop_rx_thread()
    _stop_tx_thread()
    logger.info("串口连接后台线程已停止")


__all__ = [
    "readline",
    "writeline",
    "start_backend",
    "stop_backend"
]
