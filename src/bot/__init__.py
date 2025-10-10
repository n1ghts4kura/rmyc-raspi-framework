#
# bot/__init__.py
#
# @author n1ghts4kura
#

from . import blaster
from . import chassis
from . import conn
from . import game_msg
from . import gimbal
from . import robot
from . import sdk


def restore_robot_state(delay: bool = True):
    """恢复机器人初始状态"""
    if delay:
        import time
        time.sleep(2)  # 等待2秒，确保之前的命令都已发送完毕
    chassis.set_chassis_speed_3d(0, 0, 0)  # 停止底盘
    gimbal.set_gimbal_recenter(delay=delay)  # 云台回中
    gimbal.set_gimbal_speed(0, 0, delay=delay)  # 停止云台转动


__all__ = [
    "blaster",
    "chassis",
    "conn",
    "game_msg",
    "gimbal",
    "robot",
    "sdk",
]
