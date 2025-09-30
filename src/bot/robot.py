#
# bot/robot.py
# 用于处理机器人运动模式。

from typing import Literal

import conn as serial

ROBOT_MODES = (
    "chassis_lead", # 云台跟随底盘
    "gimbal_lead",  # 底盘跟随云台
    "free" # 自由模式
)

def set_robot_mode(mode: Literal["chassis_lead", "gimbal_lead", "free"] = "free") -> bool:
    """
    设置机器人运动模式
    Args:
        mode (Literal["chassis_lead", "gimbal_lead", "free"]): 机器人模式
            - "chassis_lead": 云台跟随底盘
            - "gimbal_lead": 底盘跟随云台
            - "free": 自由模式
    Returns:
        bool: 是否成功设置模式
    """
    if mode not in ROBOT_MODES:
        return False

    serial.write_serial(f"robot mode {mode};")
    return True

__all__ = [
    "set_robot_mode",
]
