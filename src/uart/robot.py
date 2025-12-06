# robot.py
# 机器人运动控制模块
#
# @author n1ghts4kura
# @date 25-12-6
#


from typing import Literal

from . import conn


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

    conn.writeline(f"robot mode {mode};")
    return True


__all__ = [
    "set_robot_mode",
]