#
# robot/gimbal.py
# 云台控制模块
#
# @author n1ghts4kura
#

from . import conn

def set_gimbal_speed(
    pitch: float,
    yaw: float
) -> None:
    """
    设置云台的速度。

    Args:
        pitch (float): 云台俯仰速度，范围[-450, 450] (°/s) 
        yaw (float):   云台偏航速度，范围[-450, 450] (°/s)
    Returns:
        None
    """
    conn.write_serial(f"gimbal speed p {pitch} y {yaw};")


def _move_gimbal(
    pitch: float | None,
    yaw: float | None,
    vpitch: float | None,
    vyaw: float | None
) -> None:
    """
    【内部函数】控制云台移动（相对角度，受 UART 下位机 ±55° 限制）。
    
    ⚠️ 此函数为底层实现，不建议直接调用
    推荐使用 rotate_gimbal() 代替（支持滑环无限旋转）

    Args:
        pitch (float):  云台俯仰角度，范围[-55, 55] (°)
        yaw (float):    云台偏航角度，范围[-55, 55] (°)
        vpitch (float): 云台俯仰速度，范围[0, 540] (°/s)
        vyaw (float):   云台偏航速度，范围[0, 540] (°/s)
    Raises:
        ValueError: 如果所有角度和速度参数都为 None 或 参数不在范围内。
    """

    if (pitch is not None and not (-55 <= pitch <= 55)) or \
       (yaw is not None and not (-55 <= yaw <= 55)) or \
       (vpitch is not None and not (0 <= vpitch <= 540)) or \
       (vyaw is not None and not (0 <= vyaw <= 540)):
        raise ValueError("参数不在范围内。")

    all_none: bool = True
    command = "gimbal move "

    if pitch is not None:
        all_none = False
        command += f"p {pitch} "
    if yaw is not None:
        all_none = False
        command += f"y {yaw} "
    if vpitch is not None:
        all_none = False
        command += f"vp {vpitch} "
    if vyaw is not None:
        all_none = False
        command += f"vy {vyaw} "

    if all_none:
        raise ValueError("At least one of pitch, yaw, vpitch, or vyaw must be provided.")

    command += ";"
    conn.write_serial(command)


def _move_gimbal_absolute(
    pitch: float | None,
    yaw: float | None,
    vpitch: int | None,
    vyaw: int | None
) -> None:
    """
    【内部函数】控制云台绝对移动（受硬件限制：pitch ∈ [-25, 30]°, yaw ∈ [-250, 250]°）。
    
    ⚠️ 此函数为底层实现，不建议直接调用
    推荐使用 rotate_gimbal_absolute() 代替（支持滑环无限旋转）

    Args:
        pitch (float):  云台俯仰角度，范围[-25, 30] (°)
        yaw (float):    云台偏航角度，范围[-250, 250] (°)
        vpitch (int):   云台俯仰速度，范围[0, 540] (°/s)
        vyaw (int):     云台偏航速度，范围[0, 540] (°/s)
    Raises:
        ValueError: 如果所有角度和速度参数都为 None 或 参数不在范围内。
    """

    if (pitch is not None and not (-25 <= pitch <= 30)) or \
       (yaw is not None and not (-250 <= yaw <= 250)) or \
       (vpitch is not None and not (0 <= vpitch <= 540)) or \
       (vyaw is not None and not (0 <= vyaw <= 540)):
        raise ValueError("参数不在范围内。")

    all_none = True
    command = "gimbal moveto "

    if pitch is not None:
        all_none = False
        command += f"p {pitch} "
    if yaw is not None:
        all_none = False
        command += f"y {yaw} "
    if vpitch is not None:
        all_none = False
        command += f"vp {vpitch} "
    if vyaw is not None:
        all_none = False
        command += f"vy {vyaw} "

    if all_none:
        raise ValueError("At least one of pitch, yaw, vpitch, or vyaw must be provided.")

    command += ";"
    conn.write_serial(command)    


def set_gimbal_suspend() -> None:
    """
    挂起云台。
    """
    conn.write_serial("gimbal suspend;")


def set_gimbal_resume() -> None:
    """
    恢复云台。
    """
    conn.write_serial("gimbal resume;")


def set_gimbal_recenter() -> None:
    """
    云台回中。
    """
    # serial.write_serial("gimbal recenter;")
    _move_gimbal_absolute(0, 0, 90, 90)


def rotate_gimbal(
    pitch: float | None = None,
    yaw: float | None = None,
    vpitch: float | None = None,
    vyaw: float | None = None
) -> None:
    """
    【主操作函数】控制云台旋转（相对角度模式，支持滑环 360° 无限旋转）。
    
    功能说明：
        - 由于 UART 下位机只能接受有限范围的角度输入（±55°），
          本函数会将大角度分解为多个小角度步进指令。
        - 适用于安装滑环后的云台，理论上可以旋转任意角度。
    
    工作原理：
        1. 如果输入角度在 ±50° 范围内，直接调用 move_gimbal()
        2. 如果超出范围，分解为多个 ±50° 的步进 + 余数角度
        3. 每次步进后等待短暂时间，确保云台跟上指令
    
    Args:
        pitch (float):  云台俯仰角度（相对角度，度），无范围限制
        yaw (float):    云台偏航角度（相对角度，度），无范围限制
        vpitch (float): 云台俯仰速度，范围[0, 540] (°/s)
        vyaw (float):   云台偏航速度，范围[0, 540] (°/s)
    
    Raises:
        ValueError: 如果所有角度和速度参数都为 None 或速度参数不在范围内。
    
    Example:
        >>> # 云台向右旋转 180°（需要滑环支持）
        >>> move_gimbal_360(yaw=180, vyaw=90)
        >>> 
        >>> # 云台向左旋转 270°
        >>> move_gimbal_360(yaw=-270, vyaw=90)
    
    注意事项：
        - 本函数会阻塞执行，直到所有步进完成
        - 大角度旋转需要较长时间，建议在独立线程中调用
        - 确保机器人已安装滑环，否则可能损坏硬件限位卡扣
        - 推荐用于自瞄系统等需要大范围快速转动的场景
    """
    import time
    
    # 参数验证
    if (vpitch is not None and not (0 <= vpitch <= 540)) or \
       (vyaw is not None and not (0 <= vyaw <= 540)):
        raise ValueError("速度参数不在范围内: vpitch, vyaw 必须在 [0, 540] (°/s)")
    
    if pitch is None and yaw is None:
        raise ValueError("至少需要提供 pitch 或 yaw 参数")
    
    # 下位机单次可接受的最大角度（留有安全余量）
    MAX_STEP_ANGLE = 50.0
    
    # 处理 pitch（俯仰角）
    if pitch is not None:
        remaining_pitch = pitch
        
        while abs(remaining_pitch) > MAX_STEP_ANGLE:
            # 计算本次步进角度（带符号）
            step = MAX_STEP_ANGLE if remaining_pitch > 0 else -MAX_STEP_ANGLE
            
            # 发送步进指令
            _move_gimbal(
                pitch=step,
                yaw=None,
                vpitch=vpitch,
                vyaw=None
            )
            
            # 等待云台运动（根据速度估算时间 + 安全余量）
            if vpitch is not None and vpitch > 0:
                wait_time = abs(step) / vpitch + 0.1  # 秒
                time.sleep(wait_time)
            else:
                time.sleep(0.5)  # 默认等待时间
            
            remaining_pitch -= step
        
        # 发送剩余角度
        if abs(remaining_pitch) > 0.1:  # 避免微小角度指令
            _move_gimbal(
                pitch=remaining_pitch,
                yaw=None,
                vpitch=vpitch,
                vyaw=None
            )
            if vpitch is not None and vpitch > 0:
                time.sleep(abs(remaining_pitch) / vpitch + 0.1)
            else:
                time.sleep(0.3)
    
    # 处理 yaw（偏航角）
    if yaw is not None:
        remaining_yaw = yaw
        
        while abs(remaining_yaw) > MAX_STEP_ANGLE:
            # 计算本次步进角度（带符号）
            step = MAX_STEP_ANGLE if remaining_yaw > 0 else -MAX_STEP_ANGLE
            
            # 发送步进指令
            _move_gimbal(
                pitch=None,
                yaw=step,
                vpitch=None,
                vyaw=vyaw
            )
            
            # 等待云台运动（根据速度估算时间 + 安全余量）
            if vyaw is not None and vyaw > 0:
                wait_time = abs(step) / vyaw + 0.1  # 秒
                time.sleep(wait_time)
            else:
                time.sleep(0.5)  # 默认等待时间
            
            remaining_yaw -= step
        
        # 发送剩余角度
        if abs(remaining_yaw) > 0.1:  # 避免微小角度指令
            _move_gimbal(
                pitch=None,
                yaw=remaining_yaw,
                vpitch=None,
                vyaw=vyaw
            )
            if vyaw is not None and vyaw > 0:
                time.sleep(abs(remaining_yaw) / vyaw + 0.1)
            else:
                time.sleep(0.3)


def rotate_gimbal_absolute(
    pitch: float | None = None,
    yaw: float | None = None,
    vpitch: float | None = None,
    vyaw: float | None = None
) -> None:
    """
    【主操作函数】控制云台旋转（绝对角度模式，支持滑环 360° 无限旋转）。
    
    功能说明：
        - 相比 move_gimbal_360()，本函数使用绝对角度控制
        - 由于下位机绝对角度限制（pitch: [-25, 30]°, yaw: [-250, 250]°），
          超出范围的角度会被分解为步进控制
        - 适用于需要精确到达指定绝对位置的场景
    
    工作原理：
        1. 对于 yaw 角度，如果在 [-250, 250]° 范围内，直接调用 move_gimbal_absolute()
        2. 如果超出范围，计算相对偏移量，调用 move_gimbal_360() 分步执行
        3. 对于 pitch 同理（范围 [-25, 30]°）
    
    Args:
        pitch (float):  云台俯仰角度（绝对角度，度），无范围限制
        yaw (float):    云台偏航角度（绝对角度，度），无范围限制
        vpitch (float): 云台俯仰速度，范围[0, 540] (°/s)
        vyaw (float):   云台偏航速度，范围[0, 540] (°/s)
    
    Raises:
        ValueError: 如果所有角度和速度参数都为 None 或速度参数不在范围内。
    
    Example:
        >>> # 云台转到绝对角度 yaw=300°（需要滑环支持）
        >>> move_gimbal_360_absolute(yaw=300, vyaw=90)
        >>> 
        >>> # 云台转到绝对角度 yaw=-300°
        >>> move_gimbal_360_absolute(yaw=-300, vyaw=90)
    
    注意事项：
        - 本函数会阻塞执行，直到运动完成
        - 超出下位机绝对角度范围时，会转换为相对角度分步执行
        - 确保机器人已安装滑环
        - ⚠️ 警告：由于使用相对角度逼近，可能存在累积误差
    """
    # 参数验证
    if (vpitch is not None and not (0 <= vpitch <= 540)) or \
       (vyaw is not None and not (0 <= vyaw <= 540)):
        raise ValueError("速度参数不在范围内: vpitch, vyaw 必须在 [0, 540] (°/s)")
    
    if pitch is None and yaw is None:
        raise ValueError("至少需要提供 pitch 或 yaw 参数")
    
    # 下位机绝对角度限制
    PITCH_MIN, PITCH_MAX = -25.0, 30.0
    YAW_MIN, YAW_MAX = -250.0, 250.0
    
    # 处理 pitch（俯仰角）
    if pitch is not None:
        if PITCH_MIN <= pitch <= PITCH_MAX:
            # 在范围内，直接使用绝对角度控制
            _move_gimbal_absolute(
                pitch=pitch,
                yaw=None,
                vpitch=int(vpitch) if vpitch is not None else None,
                vyaw=None
            )
        else:
            # 超出范围，使用相对角度分步控制
            # ⚠️ 注意：这里假设当前位置未知，直接使用相对偏移
            # 实际应用中可能需要查询当前云台角度
            rotate_gimbal(
                pitch=pitch,
                yaw=None,
                vpitch=vpitch,
                vyaw=None
            )
    
    # 处理 yaw（偏航角）
    if yaw is not None:
        if YAW_MIN <= yaw <= YAW_MAX:
            # 在范围内，直接使用绝对角度控制
            _move_gimbal_absolute(
                pitch=None,
                yaw=yaw,
                vpitch=None,
                vyaw=int(vyaw) if vyaw is not None else None
            )
        else:
            # 超出范围，使用相对角度分步控制
            rotate_gimbal(
                pitch=None,
                yaw=yaw,
                vpitch=None,
                vyaw=vyaw
            )


__all__ = [
    "set_gimbal_speed",
    "set_gimbal_suspend",
    "set_gimbal_resume",
    "set_gimbal_recenter",
    "rotate_gimbal",           # 主操作函数：相对角度旋转（支持滑环 360°）
    "rotate_gimbal_absolute"   # 主操作函数：绝对角度旋转（支持滑环 360°）
]
