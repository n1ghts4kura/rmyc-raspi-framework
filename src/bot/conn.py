#
# serial.py
#
# @author n1ghts4kura
# @date 2025/9/28
#

import os
import serial as s
from threading import Lock

import logger as LOG

# uart连接配置
serial_conn: s.Serial | None = None
serial_conn_lock = Lock()

def init_serial() -> bool:
    """
    初始化UART连接
    """
    
    os.system("sudo chmod 777 /dev/ttyAMA0") # 设置设备权限

    global serial_conn
    serial_conn = s.Serial(
        port="/dev/ttyAMA0",
        baudrate=115200,
        bytesize=s.EIGHTBITS,
        parity=s.PARITY_NONE,
        stopbits=s.STOPBITS_ONE,
        timeout=10,
    )

    return serial_conn.is_open

def read_serial() -> str:
    """
    从UART读取数据
    Returns:
        str: 读取到的数据
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
        except s.SerialException as e:
            LOG.exception("Serial write error: %s", e)
    
    return False

__all__ = ["read_serial", "write_serial", ]
