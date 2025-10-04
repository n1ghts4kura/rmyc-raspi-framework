#
# aimassistant/pipeline.py
# 自瞄 工作管线
#
# @author n1ghts4kura
# @date 2025/10/3
#


import logger as LOG
import config

from recognizer import Recognizer
from bot.gimbal import rotate_gimbal, set_gimbal_recenter
from aimassistant.selector import selector_v1
from aimassistant.angle import calculate_angles


def aim_step_v1(recognizer: Recognizer) -> bool:
    """
    执行一次自瞄步骤（检测 → 选择 → 解算 → 控制）。
    注意事项：
        - 本函数为非阻塞设计，不等待云台运动完成
    
    Args:
        recognizer: 视觉识别器实例（需已启动）
    Returns:
        bool: 是否成功瞄准目标
            - True: 检测到目标并已发送控制指令
            - False: 未检测到目标或识别器未就绪
    """

    # 获取最新的检测框
    boxes = recognizer.get_latest_boxes()
    
    # 无检测结果时返回
    if boxes is None or len(boxes) == 0:
        return False
    
    # 选择最优目标
    best_box = selector_v1(boxes)
    if best_box is None:
        LOG.debug("selector_v1 返回 None，无有效目标")
        return False
    
    # 解算云台角度偏差
    yaw_offset, pitch_offset = calculate_angles(best_box)
    
    # 控制云台运动（相对角度模式，支持滑环360°旋转）
    rotate_gimbal(
        pitch=pitch_offset,
        yaw=yaw_offset,
        vpitch=config.GIMBAL_SPEED,
        vyaw=config.GIMBAL_SPEED
    )
    
    LOG.debug(f"自瞄控制: yaw={yaw_offset:.2f}°, pitch={pitch_offset:.2f}°")
    return True
