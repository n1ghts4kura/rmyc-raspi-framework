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

    # **ATTENTION*
    # 在使用usb-to-ttl工具前
    # YOU SHOULD KNOW:
    #
    # `lsusb` 是用来检测usb接口上接了什么东西的
    # `ls /dev/tty*` 是用来检测串口端口映射情况的
    # 请在使用前执行以下步骤
    # 1. 补药接上usb-to-ttl转接器 使用`lsusb` `ls /dev/tty*`指令
    # 2. 接上转接器 再使用上述指令
    # 重复这两个步骤，直到你知道这个转接口对应的端口到底是/dev/ttyACM0 还是/dev/ttyS0 还是/dev/ttyUSB0 还是......
    # 然后根据这一台树莓派使用的转接口（每个转接口对应的端口大概率不一样！！）
    # 设置_device_address变量
    _device_address = "/dev/ttyUSB0" 
    os.system(f"sudo chmod 777 {_device_address}") # 设置设备权限

    global serial_conn
    serial_conn = s.Serial(
        port=_device_address,
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
