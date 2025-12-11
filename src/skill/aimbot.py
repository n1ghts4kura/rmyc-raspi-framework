# aimbot.py
# 自瞄技能
#
# @author n1ghts4kura
# @date 25-12-7
#

import time

from src import config
from src.uart import gimbal, blaster
from src.skill.base import BaseSkill
from src.vision.camera import Camera
from src.vision.detector.gimbal import GimbalDetector
from src.aimbot.selector import selector_v1
from src import logger


def static_aimbot_action(skill: BaseSkill) -> None:
    """
    **静态自瞄**

    Args:
        skill: 技能对象，包含当前检测结果和其他相关信息。
    """

    # 获取摄像头和检测器实例
    cam = Camera()
    if not cam.open():
        logger.error("摄像头打开失败")
        return

    detector = GimbalDetector()
    if not detector.initialize():
        logger.error("装甲板检测器初始化失败")
        return

    logger.info("自瞄启动")

    while not skill.cancel_event.is_set():

        start_time = time.time()

        # 获取当前帧
        ret, frame = cam.read()
        # 跳过无效帧
        if not ret or frame is None:
            if skill.cancel_event.is_set():
                break
            logger.warning("摄像头帧读取失败")
            time.sleep(0.05)
            continue

        # 进行目标检测
        detection_result = detector.detect(frame)
        # 跳过无效检测结果
        if len(detection_result) == 0:
            # **重置PID控制器状态**
            config.AIMBOT_HOR_PID.reset()
            config.AIMBOT_VER_PID.reset()
            logger.info("检测不到目标 重置PID...")
            continue
        else:
            logger.debug(f"检测到 {len(detection_result)} 个目标")
        
        # 获取到应该击打的装甲板box
        target = selector_v1(detection_result) # **请确保detection_result非空**

        # 计算距离屏幕中心偏移量
        dxn = target.xywhn[0] - 0.5
        dyn = target.xywhn[1] - 0.5
        ctrl_x = ctrl_y = None
        x_ok = y_ok = False

        # 判断是否进入死区
        if abs(dxn) > config.AIMBOT_DEADZONE_X_MIN and abs(dxn) < config.AIMBOT_DEADZONE_X_MAX:
            # x_min < |dxn| < x_max，进行水平调整
            ctrl_x = config.AIMBOT_HOR_PID(dxn)
        else:
            x_ok = True # 水平瞄准完成

        if abs(dyn) > config.AIMBOT_DEADZONE_Y_MIN and abs(dyn) < config.AIMBOT_DEADZONE_Y_MAX:
            # y_min < |dyn| < y_max，进行垂直调整
            ctrl_y = config.AIMBOT_VER_PID(dyn)
        else:
            y_ok = True # 垂直瞄准完成
        
        logger.info(f"dxn: {dxn:.4f} dyn: {dyn:.4f} ctrl_x: {ctrl_x} ctrl_y: {ctrl_y}")

        # 发送云台控制指令
        if not x_ok or not y_ok:
            gimbal.rotate_gimbal(ctrl_y, ctrl_x)
        else:
            logger.info("目标已锁定，准备开火")
            break

        # 控制动作频率
        elapsed = time.time() - start_time
        if elapsed < config.AIMBOT_ACTION_DELAY:
            time.sleep(config.AIMBOT_ACTION_DELAY - elapsed)
    
    # 瞄准完成，开火
    while not skill.cancel_event.is_set():
        blaster.blaster_fire()
        time.sleep(0.33) # 每秒3发

    logger.info("已收到停止信号，停止射击")


skill = BaseSkill(
    binding_key="n", # **用小写字母注册！**
    invoke_func=static_aimbot_action,
)
        