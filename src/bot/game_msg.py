#
# robot/game_msg.py
# 赛事数据处理
#
# @author n1ghts4kura
#

from threading import Lock
import conn as serial

msg_stack = [] # 消息栈
msg_stack_lock = Lock() # 消息栈锁

def game_msg_on() -> None:
    """
    开启游戏消息接收
    """
    serial.write_serial("game msg on;")

def game_msg_off() -> None:
    """
    关闭游戏消息接收
    """
    serial.write_serial("game msg off;")

def process(data: str) -> dict:
    """
    处理接收到的游戏消息
    消息格式为：`game msg push [0, 6, 1, 0, 0, 255, 1, 199];`

    Returns:
        dict: 解析后的消息字典
    """

    global msg_stack
    rsp = {}

    data = data[15:-2]  # 去除前缀和后缀
    data_int = data.split(", ") # 转换为整数列表

    rsp["cmd_id"] = int(data_int[0])
    rsp["len"] = int(data_int[1])
    rsp["mouse_press"] = int(data_int[2])
    rsp["mouse_x"] = int(data_int[3])
    rsp["mouse_y"] = int(data_int[4])
    rsp["seq"] = int(data_int[5])
    rsp["key_num"] = int(data_int[6])
    rsp["keys"] = []
    for key in data_int[7:(7 + rsp["key_num"])]:
        rsp["keys"].append(int(key))
    
    return rsp

__all__ = [
    "game_msg_on",
    "game_msg_off",
    "process"
]
