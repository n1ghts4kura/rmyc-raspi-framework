#
# robot/game_msg.py
# 赛事数据处理
#
# @author n1ghts4kura
#

import typing
from threading import Lock
from . import conn

class GameMsgDictType(typing.TypedDict, total=False):
    """
    赛事数据类型
    """

    cmd_id: int # 命令ID
    len: int # 后面几种数据的长度

    mouse_press: int # 鼠标按键状态 1.右键 2.左键 4.中键 TODO("Test me wtf 4?")
    mouse_x: int # 鼠标X轴移动距离
    mouse_y: int # 鼠标Y轴移动距离

    seq: int # 包序列号 TODO("搞清楚这个是什么 2025/10/1")
    key_num: int # 按下了几个键盘按键 最多识别三个
    keys: list[str] # 按下的按键 字符列表 TODO("搞清楚数字和字符的对应关系 不是chr函数 2025/10/1")


def game_msg_on() -> None:
    """
    开启游戏消息接收
    """
    conn.write_serial("game msg on;")


def game_msg_off() -> None:
    """
    关闭游戏消息接收
    """
    conn.write_serial("game msg off;")


def game_msg_process(data: str) -> GameMsgDictType:
    """
    处理接收到的游戏消息  
    消息格式为：`game msg push [0, 6, 1, 0, 0, 255, 1, 199];`  
    处理后将会转化为:  
    ```
    {
        "cmd_id": 0,
        "len": 6,
        "mouse_press": 1,
        "mouse_x": 0,
        "mouse_y": 0,
        "seq": 255,
        "key_num": 1,
        "keys": ["199"]
    }
    ```

    Returns:
        dict: 解析后的消息字典
    """

    global msg_stack
    rsp: GameMsgDictType = {}

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
        # TODO 在这里实现 **真实的** **正确的** *数字对应字符* 的逻辑 2025/10/1
        int_to_str_key_func = lambda x: chr(int(x) - 80) # 小写字母!!
        rsp["keys"].append(int_to_str_key_func(key))

        #
        # *n1ghts4kura* 2025/10/1
        # GPT5-Codex:
        # 我先看了一圈这个数字和字母的关系，发现 199 与字符 w 的差值正好是 80：
        # [ 199 - \text{ord}('w') = 199 - 119 = 80 ]
        #
        # 这里的 ord() 是 Python 里的函数，用来取字符的 ASCII/Unicode 码。也就是说，可以把 199 理解为“在 w 的编码基础上固定加了 80”。如果这个规律成立，那就能很自然地推广到 26 个小写英文字母：
        # 对任意小写字母 c，映射规则是
        # [ \text{encode}(c) = \text{ord}(c) + 80 ]
        # 反向解码则是
        # [ \text{decode}(n) = \text{chr}(n - 80) ]
        #
        # 这样，a（编码 97）会对应 177，z（编码 122）对应 202，中间呈现一个连续区间 [177, 202]。
        #
    
    return rsp

__all__ = [
    "game_msg_on",
    "game_msg_off",
    "game_msg_process",
    "GameMsgDictType",
]
