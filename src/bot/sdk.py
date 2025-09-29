#
# bot/sdk.py
# SDK模式控制
#
# @author: n1ghts4kura
#

import conn as serial

def enter_sdk_mode() -> None:
    """
    进入SDK模式。
    """
    serial.write_serial("command;")

def exit_sdk_mode() -> None:
    """
    退出SDK模式。
    """
    serial.write_serial("quit;")

__all__ = [
    "enter_sdk_mode",
    "exit_sdk_mode",
]
