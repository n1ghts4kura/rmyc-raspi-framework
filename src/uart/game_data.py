# game_data.py
# 赛事数据处理模块
#
# @author n1ghts4kura
# @date 25-12-6
#

import conn


def game_msg_on() -> None:
    """
    开启游戏消息接收
    """
    conn.writeline("game msg on;")


def game_msg_off() -> None:
    """
    关闭游戏消息接收
    """
    conn.writeline("game msg off;")



__all__ = [
    "game_msg_on",
    "game_msg_off",
]