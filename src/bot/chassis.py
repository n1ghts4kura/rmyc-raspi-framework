#
# robot/chassis.py
# 机器人 底盘控制模块
# **注意**：该模块存在阻塞函数，但是**默认关闭**。
#
# @author n1ghts4kura
# @date 2025/10/1
#


from . import conn


def set_chassis_speed_3d(
    speed_x: float,
    speed_y: float,
    speed_z: float
) -> None:
    """
    设置底盘的3D速度
    Args:
        speed_x (float): X轴速度，范围 -3.5 到 3.5 (speed_x > 0 向前)
        speed_y (float): Y轴速度，范围 -3.5 到 3.5 (speed_y < 0 向左)
        speed_z (float): Z轴速度，范围 -600 到 600 (单位: °/s)
    Raises:
        ValueError: 如果速度不在指定范围内
    """

    if not (speed_x >= -3.5 and speed_x <= 3.5):
        raise ValueError("speed_x must be between -3.5 and 3.5")
    if not (speed_y >= -3.5 and speed_y <= 3.5):
        raise ValueError("speed_y must be between -3.5 and 3.5")
    if not (speed_z >= -600 and speed_z <= 600):
        raise ValueError("speed_z must be between -600 and 600")

    conn.write_serial(f"chassis speed x {speed_x} y {speed_y} z {speed_z};")


def set_chassis_wheel_speed(
    w1: int,
    w2: int,
    w3: int,
    w4: int
) -> None:
    """
    设置底盘四个轮子的速度
    Args:
        w1 (int): 前左轮速度，范围 -1000 到 1000 单位rpm
        w2 (int): 前右轮速度，范围 -1000 到 1000 单位rpm
        w3 (int): 后右轮速度，范围 -1000 到 1000 单位rpm
        w4 (int): 后左轮速度，范围 -1000 到 1000 单位rpm
    Raises:
        ValueError: 如果轮子速度不在指定范围内
    """

    if not all(-1000 <= w <= 1000 for w in [w1, w2, w3, w4]):
        raise ValueError("Wheel speeds must be between -1000 and 1000")

    conn.write_serial(f"chassis wheel w1 {w1} w2 {w2} w3 {w3} w4 {w4};")


def chassis_move(
    distance_x: float,
    distance_y: float,
    degree_z: int | None,
    speed_xy: float | None,
    speed_z: float | None
) -> None:
    """
    控制底盘移动指定距离
    Args:
        distance_x (float): X轴移动距离，        范围[-5, 5] (m)
        distance_y (float): Y轴移动距离，        范围[-5, 5] (m)
        degree_z   (int)  : Z轴旋转角度，        范围[-1800, 1800] (°)
        speed_xy   (float): XY平面移动速度，     范围(0, 3.5] (m/s)
        speed_z    (float): Z轴旋转速度，        范围(0, 600] (°/s)
    Raises:
        ValueError: 如果不在指定范围内
    """

    if not (-5 <= distance_x <= 5):
        raise ValueError("distance_x must be between -5 and 5")
    if not (-5 <= distance_y <= 5):
        raise ValueError("distance_y must be between -5 and 5")
    if degree_z and not (-1800 <= degree_z <= 1800):
        raise ValueError("degree_z must be between -1800 and 1800")
    if speed_xy and not (0 < speed_xy <= 3.5):
        raise ValueError("speed_xy must be between 0 and 3.5")
    if speed_z and not (0 < speed_z <= 600):
        raise ValueError("speed_z must be between 0 and 600")
    
    command = f"chassis move x {distance_x} y {distance_y}"
    if degree_z:
        command += f" z {degree_z}"
    if speed_xy:
        command += f" vxy {speed_xy}"
    if speed_z:
        command += f" vz {speed_z}"
    command += ";"

    conn.write_serial(command)


__all__ = [
    "set_chassis_speed_3d",
    "set_chassis_wheel_speed",
    "chassis_move"
]
