#
# bot/sdk.py
# SDK模式控制
#
# @author: n1ghts4kura
#

from . import conn

def enter_sdk_mode() -> None:
    """
    进入SDK模式。
    """
    conn.write_serial("command;")


def exit_sdk_mode() -> None:
    """
    退出SDK模式。
    """
    conn.write_serial("quit;")


__all__ = [
    "enter_sdk_mode",
    "exit_sdk_mode",
]
