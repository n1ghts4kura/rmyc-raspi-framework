# aimbot.py
# 自瞄技能
#
# @author n1ghts4kura
# @date 25-12-7
#

from re import A
import time

from src import config
from src.uart import gimbal, blaster
from src.skill.base import BaseSkill
from src.vision.camera import Camera
from src.vision.detector.gimbal import GimbalDetector
from src.aimbot.selector import selector_v1


def static_aimbot_action(skill: BaseSkill) -> None:
    """
    **静态自瞄**

    Args:
        skill: 技能对象，包含当前检测结果和其他相关信息。
    """

    # 获取摄像头和检测器实例
    cam = Camera()
    detector = GimbalDetector()
    locked = False # 是否已锁定目标

    while not locked:

        start_time = time.time()

        # 获取当前帧
        ret, frame = cam.read()
        # 跳过无效帧
        if not ret or frame is None:
            continue

        # 进行目标检测
        detection_result = detector.detect(frame)
        # 跳过无效检测结果
        if len(detection_result) == 0:
            # **重置PID控制器状态**
            config.AIMBOT_HOR_PID.reset()
            config.AIMBOT_VER_PID.reset()
            continue
        
        # 获取到应该击打的装甲板box
        target = selector_v1(detection_result) # **请确保detection_result非空**

        # 计算距离屏幕中心偏移量
        dxn = target.xywhn[0] - 0.5
        dyn = target.xywhn[1] - 0.5
        ctrl_x = ctrl_y = None

        # 如果未进入死区，就继续移动云台
        if abs(dxn) > config.AIMBOT_DEADZONE_HOR:
            ctrl_x = config.AIMBOT_HOR_PID(dxn)
        if abs(dyn) > config.AIMBOT_DEADZONE_VER:
            ctrl_y = config.AIMBOT_VER_PID(dyn)

        if ctrl_x is not None or ctrl_y is not None:
            # 还有调整量，发送控制指令
            gimbal.rotate_gimbal(ctrl_y, ctrl_x, delay=False)
        else:
            # 瞄准完成，开火
            locked = True

        # 控制动作频率
        elapsed = time.time() - start_time
        if elapsed < config.AIMBOT_ACTION_DELAY:
            time.sleep(config.AIMBOT_ACTION_DELAY - elapsed)
    
    # 瞄准完成，开火
    while True:
        blaster.blaster_fire()
        time.sleep(0.2)        
        