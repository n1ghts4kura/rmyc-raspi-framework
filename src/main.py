# main.py
# 
# @author n1ghts4kura
# @date 25-12-7
#

import time

from src import logger
from src.uart import conn
from src.uart.sdk import enter_sdk_mode, exit_sdk_mode
from src.uart.dataholder import DataHolder
from src.skill import (static_aimbot_skill, example_skill, SkillManager)
from src.vision.camera import Camera
from src.vision.detector import GimbalDetector


def main() -> None:

    print(
        r"""
                                       _     ___                                 _   
 ___ _____ _ _ ___ ___ ___ ___ ___ ___|_|___|  _|___ ___ _____ ___ _ _ _ ___ ___| |_ 
|  _|     | | |  _|___|  _| .'|_ -| . | |___|  _|  _| .'|     | -_| | | | . |  _| '_|
|_| |_|_|_|_  |___|   |_| |__,|___|  _|_|   |_| |_| |__,|_|_|_|___|_____|___|_| |_,_|
          |___|                   |_|                                                
     ___     ___                                                                     
 _ _|_  |   |_  |                                                                    
| | |_| |_ _|  _|                                                                    
 \_/|_____|_|___|                                                                    
         """
    )

    time.sleep(1)

    logger.info("rmyc-raspi-framework v1.2 启动中...")

    # == 初始化摄像头 ===
    cam = Camera()

    if not cam.open():
        logger.error("摄像头打开失败！请检查连接。")
        return

    if not cam.test_opened():
        logger.error("摄像头测试帧获取失败！请检查摄像头参数设置")
        return

    logger.info(f"1. 摄像头设置完毕. [{str(cam)}]")

    # === 初始化自瞄识别器 ===
    gimbal_detector = GimbalDetector()

    if not gimbal_detector.initialize():
        logger.error("自瞄识别器初始化失败！")
        return

    logger.info("2. 自瞄识别器初始化完毕.")
    
    # === 初始化串口 ===
    if not conn.open_serial():
        logger.error("串口打开失败！请检查连接。")
        return

    if not conn.handshake_serial():
        logger.error("串口握手失败！请检查连接。")
        return

    conn.start_rx_thread()
    enter_sdk_mode()
    logger.info("3. 串口连接已建立.")
    
    # === 初始化数据存储器 ===
    data_holder = DataHolder()

    logger.info("4. 数据存储器初始化完毕.")

    # === 初始化技能管理器 ===
    skill_manager = SkillManager()
    skill_manager.add_skill(example_skill)
    skill_manager.add_skill(static_aimbot_skill)

    logger.info("5. 技能管理器初始化完毕.")

    logger.info("所有模块初始化完毕.")
    time.sleep(1)
    logger.info("3...")
    time.sleep(1)
    logger.info("2..")
    time.sleep(1)
    logger.info("1.")
    time.sleep(1)
    logger.info("启动.")

    time.sleep(1)
    conn.rx_queue.put("game msg push [0, 6, 1, 0, 0, 255, 1, 199];")

    try:
        while True:
            data_holder.fetch_and_process() # 获取比赛数据
            pressed_keys = data_holder.pressed_keys # 获取按键信息

            if len(pressed_keys) > 0:
                for key in pressed_keys:
                    if skill_manager.get_skill_enabled_state(key):
                        skill_manager.cancel_skill_by_key(key)
                    else:
                        skill_manager.invoke_skill_by_key(key)
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("收到退出信号，正在关闭...")
    finally:
        cam.close()
        exit_sdk_mode()


if __name__ == "__main__":
    main()