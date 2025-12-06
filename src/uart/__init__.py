# __init__.py
#
# @author n1ghts4kura
# @date 25-12-6
#

import time

from . import blaster
from . import chassis
from . import conn
from . import dataholder
from . import game_data
from . import gimbal
from . import robot
from . import sdk


def reset_robot_sw() -> None:
    """
    重置机器人运动状态 (自定义)
    """

    time.sleep(2) # 等待所有指令发送完毕 (虽然不知道是干嘛的。)
    chassis.set_chassis_speed_3d(0, 0, 0) # 停止底盘
    gimbal.set_gimbal_recenter(delay=True) # 云台回中
    gimbal.set_gimbal_speed(0, 0, delay=True) # 设置云台速度


__all__ = [
    "blaster",
    "chassis",
    "conn",
    "dataholder",
    "game_data",
    "gimbal",
    "robot",
    "sdk",
    "reset_robot_sw",
]