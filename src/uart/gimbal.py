# gimbal.py
# 云台控制
#
# @author n1ghts4kura
# @date 25-12-6
#


import time

from . import conn


def set_gimbal_speed(
    pitch: float,
    yaw: float,
    delay: bool = True
) -> None:
    """
    设置云台的速度。
    **注意**：调用该函数后需要一段大延迟( t = 360° / speed )，云台会按照该速度巡航一次。

    Args:
        pitch (float): 云台俯仰速度，范围[-450, 450] (°/s) 
        yaw (float):   云台偏航速度，范围[-450, 450] (°/s)
    """

    conn.writeline(f"gimbal speed p {pitch} y {yaw};")
    if delay:
        # 速度为 0 时不需要延时（停止云台运动）
        if pitch == 0 and yaw == 0:
            return
        time.sleep( 360 / max(abs(pitch), abs(yaw), 2) )  # 等待一圈巡航完成，至少等待1秒
    set_gimbal_recenter()  # 巡航完成后回中


def _move_gimbal(
    pitch: float | None,
    yaw: float | None,
    vpitch: float | None,
    vyaw: float | None,
) -> None:
    """
    【内部函数】控制云台移动（相对角度，受 UART 下位机 ±55° 限制）。非阻塞。
    
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
    conn.writeline(command)


def _move_gimbal_absolute(
    pitch: float | None,
    yaw: float | None,
    vpitch: int | None,
    vyaw: int | None
) -> None:
    """
    【内部函数】控制云台绝对移动（受硬件限制：pitch ∈ [-25, 30]°, yaw ∈ [-250, 250]°）。非阻塞。
    
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
    conn.writeline(command)    


def set_gimbal_suspend() -> None:
    """
    挂起云台。
    """
    conn.writeline("gimbal suspend;")


def set_gimbal_resume() -> None:
    """
    恢复云台。
    """
    conn.writeline("gimbal resume;")


def set_gimbal_recenter(delay: bool = True) -> None:
    """
    云台回中（pitch=0°, yaw=0°）。
    
    注意：官方 'gimbal recenter;' 指令在竖直方向上无法正常工作，
    因此使用内部 _move_gimbal_absolute(0, 0, 180, 180) 实现。
    """
    # conn.writeline("gimbal recenter;")  # 官方指令不可靠
    _move_gimbal_absolute(0, 0, 180, 180)
    if delay:
        # 计算回中所需时间：假设最大偏移 55°，速度 180°/s
        time.sleep(55 / 180 + 0.5)  # 约 0.8 秒


def rotate_gimbal(
    pitch: float | None = None,
    yaw: float | None = None,
    vpitch: float | None = None,
    vyaw: float | None = None,
    delay: bool = True
) -> None:
    """
    【主操作函数】控制云台旋转（相对角度模式，支持滑环 360° 无限旋转）。
    
    Args:
        pitch (float):  云台俯仰角度（相对角度，度），范围 [-55, 55]°（硬件限制）
        yaw (float):    云台偏航角度（相对角度，度），无范围限制（滑环支持）
        vpitch (float): 云台俯仰速度，范围[0, 540] (°/s)
        vyaw (float):   云台偏航速度，范围[0, 540] (°/s)
        delay (bool):   是否在函数内等待旋转完成（大角度旋转会阻塞较长时间）
    Raises:
        ValueError: 如果所有角度和速度参数都为 None 或速度参数不在范围内。
    Example:
        >>> # 云台向右旋转 180°（需要滑环支持）
        >>> move_gimbal_360(yaw=180, vyaw=90)
        >>> # 云台向左旋转 270°
        >>> move_gimbal_360(yaw=-270, vyaw=90)

    功能说明：
        - 由于 UART 下位机只能接受有限范围的角度输入（±55°），
          本函数会将大角度分解为多个小角度步进指令。
        - 适用于安装滑环后的云台，理论上可以旋转任意角度。
    工作原理：
        1. 如果输入角度在 ±50° 范围内，直接调用 move_gimbal()
        2. 如果超出范围，分解为多个 ±50° 的步进 + 余数角度
        3. 每次步进后等待短暂时间，确保云台跟上指令
    注意事项：
        - 本函数会阻塞执行，直到所有步进完成
        - 大角度旋转需要较长时间，建议在独立线程中调用
        - 确保机器人已安装滑环，否则可能损坏硬件限位卡扣
        - 推荐用于自瞄系统等需要大范围快速转动的场景
    """
    
    # 参数验证
    if (vpitch is not None and not (0 <= vpitch <= 540)) or \
       (vyaw is not None and not (0 <= vyaw <= 540)):
        raise ValueError("速度参数不在范围内: vpitch, vyaw 必须在 [0, 540] (°/s)")
    
    if pitch is None and yaw is None:
        raise ValueError("至少需要提供 pitch 或 yaw 参数")
    
    # 下位机单次可接受的最大角度（留有安全余量）
    MAX_STEP_ANGLE = 50.0
    
    # Pitch 轴硬件限制（俯仰轴不能无限旋转）
    PITCH_MIN, PITCH_MAX = -55.0, 55.0
    
    # 1️⃣ 验证并处理 pitch
    final_pitch = None
    pitch_error = None
    
    if pitch is not None:
        if not (PITCH_MIN <= pitch <= PITCH_MAX):
            # 超出范围，裁剪并记录错误（稍后抛出）
            final_pitch = max(PITCH_MIN, min(PITCH_MAX, pitch))
            pitch_error = ValueError(
                f"Pitch 超出硬件限制 [{PITCH_MIN}, {PITCH_MAX}]°: {pitch}°\n"
                f"已裁剪到 {final_pitch}° 并执行，但请检查您的输入角度。\n"
                f"提示：俯仰轴不支持无限旋转（仅 yaw 偏航轴支持滑环 360° 旋转）。"
            )
        else:
            final_pitch = pitch
    
    # 2️⃣ 处理 yaw（归一化到最短路径）
    if yaw is not None:
        # 归一化到 [-180, 180)，选择最短路径
        remaining_yaw = ((yaw + 180) % 360) - 180
        
        # 3️⃣ 判断是否需要分步执行
        if abs(remaining_yaw) <= MAX_STEP_ANGLE:
            # 小角度，pitch 和 yaw 可以一次性发送
            _move_gimbal(
                pitch=final_pitch,
                yaw=remaining_yaw,
                vpitch=vpitch,
                vyaw=vyaw
            )
        else:
            # 大角度，需要分步（⚠️ 会阻塞执行）
            # 第一步：同时发送 pitch 和 yaw 的首个步进
            first_yaw_step = MAX_STEP_ANGLE if remaining_yaw > 0 else -MAX_STEP_ANGLE
            _move_gimbal(
                pitch=final_pitch,  # pitch 只在第一次发送
                yaw=first_yaw_step,
                vpitch=vpitch,
                vyaw=vyaw
            )
            
            # 等待第一步完成
            if vyaw is not None and vyaw > 0:
                wait_time = abs(first_yaw_step) / vyaw + 0.1
                time.sleep(wait_time)
            else:
                time.sleep(0.5)
            
            remaining_yaw -= first_yaw_step
            
            # 后续步骤：只发送 yaw（pitch 已经到位）
            while abs(remaining_yaw) > MAX_STEP_ANGLE:
                step = MAX_STEP_ANGLE if remaining_yaw > 0 else -MAX_STEP_ANGLE
                
                _move_gimbal(
                    pitch=None,  # 后续步骤不再发送 pitch
                    yaw=step,
                    vpitch=None,
                    vyaw=vyaw
                )
                
                if vyaw is not None and vyaw > 0:
                    wait_time = abs(step) / vyaw + 0.1
                    time.sleep(wait_time)
                else:
                    time.sleep(0.5)
                
                remaining_yaw -= step
            
            # 发送最后的余数角度
            if abs(remaining_yaw) > 0.1:
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
    else:
        # 只有 pitch，没有 yaw
        if final_pitch is not None:
            _move_gimbal(
                pitch=final_pitch,
                yaw=None,
                vpitch=vpitch,
                vyaw=None
            )
    
    # 等待
    if delay:
        max_angle = max(abs(pitch) if pitch is not None else 0,
                        abs(yaw) if yaw is not None else 0)
        max_speed = max(vpitch if vpitch is not None else 0,
                        vyaw if vyaw is not None else 0,
                        1)  # 避免除零
        wait_time = max_angle / max_speed
        time.sleep(wait_time)


def rotate_gimbal_absolute(
    pitch: float | None = None,
    yaw: float | None = None,
    vpitch: float | None = None,
    vyaw: float | None = None,
    delay: bool = True
) -> None:
    """
    【主操作函数】控制云台旋转（绝对角度模式，支持滑环 360° 无限旋转）。

    Args:
        pitch (float):  云台俯仰角度（绝对角度，度），范围 [-25, 30]°（硬件限制）
        yaw (float):    云台偏航角度（绝对角度，度），范围 [-250, 250]°（下位机限制，超出时自动转为相对角度）
        vpitch (float): 云台俯仰速度，范围[0, 540] (°/s)
        vyaw (float):   云台偏航速度，范围[0, 540] (°/s)
        delay (bool):   是否在函数内等待旋转完成（大角度旋转会阻塞较长时间）
    Raises:
        ValueError: 如果所有角度和速度参数都为 None 或速度参数不在范围内。
    Example:
        >>> # 云台转到绝对角度 yaw=300°（需要滑环支持）
        >>> move_gimbal_360_absolute(yaw=300, vyaw=90)
        >>> # 云台转到绝对角度 yaw=-300°
        >>> move_gimbal_360_absolute(yaw=-300, vyaw=90)
    
    功能说明：
        - 相比 move_gimbal_360()，本函数使用绝对角度控制
        - 由于下位机绝对角度限制（pitch: [-25°, 30°], yaw: 无），
          超出范围的角度会被分解为步进控制
        - 适用于需要精确到达指定绝对位置的场景
    工作原理：
        1. 对于 yaw 角度，如果在 [-250, 250]° 范围内，直接调用 move_gimbal_absolute()
        2. 如果超出范围，计算相对偏移量，调用 move_gimbal_360() 分步执行
        3. 对于 pitch 同理（范围 [-25, 30]°）
    注意事项：
        - 本函数会阻塞执行，直到运动完成
        - 超出下位机绝对角度范围时，会转换为相对角度分步执行
        - 确保机器人已安装滑环
        - ⚠️ 警告：由于使用相对角度逼近，**可能存在累积误差**。
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
    MAX_STEP_ANGLE = 50.0  # 相对角度的最大步进
    
    # 1️⃣ 验证并处理 pitch
    final_pitch = None
    pitch_error = None
    use_absolute_pitch = False
    
    if pitch is not None:
        if PITCH_MIN <= pitch <= PITCH_MAX:
            # 在绝对角度范围内，直接使用
            final_pitch = pitch
            use_absolute_pitch = True
        else:
            # 超出范围，裁剪并记录错误
            final_pitch = max(PITCH_MIN, min(PITCH_MAX, pitch))
            use_absolute_pitch = True
            pitch_error = ValueError(
                f"Pitch 绝对角度超出硬件限制 [{PITCH_MIN}, {PITCH_MAX}]°: {pitch}°\n"
                f"已裁剪到 {final_pitch}° 并执行，但请检查您的输入角度。\n"
                f"提示：俯仰轴受机械结构限制，无法到达极限角度。"
            )
    
    # 2️⃣ 处理 yaw
    if yaw is not None:
        if YAW_MIN <= yaw <= YAW_MAX:
            # 在绝对角度范围内，pitch 和 yaw 可以一次性发送
            if use_absolute_pitch:
                _move_gimbal_absolute(
                    pitch=final_pitch,
                    yaw=yaw,
                    vpitch=int(vpitch) if vpitch is not None else None,
                    vyaw=int(vyaw) if vyaw is not None else None
                )
            else:
                _move_gimbal_absolute(
                    pitch=None,
                    yaw=yaw,
                    vpitch=None,
                    vyaw=int(vyaw) if vyaw is not None else None
                )
        else:
            # 超出绝对角度范围，需要转换为相对角度分步执行
            # ⚠️ 警告：这会导致阻塞，且可能存在累积误差
            # 计算需要旋转的相对角度（简化处理，假设当前位置为 0）
            relative_yaw = yaw
            
            # 归一化到 [-180, 180)
            remaining_yaw = ((relative_yaw + 180) % 360) - 180
            
            # 分步执行（与 rotate_gimbal 类似的逻辑）
            if abs(remaining_yaw) <= MAX_STEP_ANGLE:
                # 小角度，使用相对角度控制（pitch 用绝对角度）
                if use_absolute_pitch:
                    # 先发送 pitch（绝对角度）
                    _move_gimbal_absolute(
                        pitch=final_pitch,
                        yaw=None,
                        vpitch=int(vpitch) if vpitch is not None else None,
                        vyaw=None
                    )
                    # 再发送 yaw（相对角度）
                    _move_gimbal(
                        pitch=None,
                        yaw=remaining_yaw,
                        vpitch=None,
                        vyaw=vyaw
                    )
                else:
                    _move_gimbal(
                        pitch=None,
                        yaw=remaining_yaw,
                        vpitch=None,
                        vyaw=vyaw
                    )
            else:
                # 大角度分步
                if use_absolute_pitch:
                    # 第一步：发送 pitch（绝对） + yaw 第一步（相对）
                    first_yaw_step = MAX_STEP_ANGLE if remaining_yaw > 0 else -MAX_STEP_ANGLE
                    _move_gimbal_absolute(
                        pitch=final_pitch,
                        yaw=None,
                        vpitch=int(vpitch) if vpitch is not None else None,
                        vyaw=None
                    )
                    _move_gimbal(
                        pitch=None,
                        yaw=first_yaw_step,
                        vpitch=None,
                        vyaw=vyaw
                    )
                    
                    if vyaw is not None and vyaw > 0:
                        time.sleep(abs(first_yaw_step) / vyaw + 0.1)
                    else:
                        time.sleep(0.5)
                    
                    remaining_yaw -= first_yaw_step
                
                # 后续步骤：只发送 yaw
                while abs(remaining_yaw) > MAX_STEP_ANGLE:
                    step = MAX_STEP_ANGLE if remaining_yaw > 0 else -MAX_STEP_ANGLE
                    _move_gimbal(pitch=None, yaw=step, vpitch=None, vyaw=vyaw)
                    
                    if vyaw is not None and vyaw > 0:
                        time.sleep(abs(step) / vyaw + 0.1)
                    else:
                        time.sleep(0.5)
                    
                    remaining_yaw -= step
                
                # 最后的余数
                if abs(remaining_yaw) > 0.1:
                    _move_gimbal(pitch=None, yaw=remaining_yaw, vpitch=None, vyaw=vyaw)
                    if vyaw is not None and vyaw > 0:
                        time.sleep(abs(remaining_yaw) / vyaw + 0.1)
                    else:
                        time.sleep(0.3)
    else:
        # 只有 pitch，没有 yaw
        if use_absolute_pitch:
            _move_gimbal_absolute(
                pitch=final_pitch,
                yaw=None,
                vpitch=int(vpitch) if vpitch is not None else None,
                vyaw=None
            )
    
    # 3️⃣ 如果 pitch 超限，在执行后抛出异常
    if pitch_error:
        raise pitch_error

    # 等待
    if delay:
        max_angle = max(abs(pitch) if pitch is not None else 0,
                        abs(yaw) if yaw is not None else 0)
        max_speed = max(vpitch if vpitch is not None else 0,
                        vyaw if vyaw is not None else 0,
                        1)  # 避免除零
        wait_time = max_angle / max_speed
        time.sleep(wait_time)


__all__ = [
    "set_gimbal_speed",
    "set_gimbal_suspend",
    "set_gimbal_resume",
    "set_gimbal_recenter",
    "rotate_gimbal",           # 主操作函数：相对角度旋转（支持滑环 360°）
    "rotate_gimbal_absolute"   # 主操作函数：绝对角度旋转（支持滑环 360°）
]