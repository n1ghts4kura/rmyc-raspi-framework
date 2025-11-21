#
# data_collector.py
# 数据采集工具
#
# @author n1ghts4kura
# @date 2025-11-21
#

import os
import cv2
import time
import threading
from datetime import datetime

from src.logger import logger


SAVE_PATH = "training/data/origin"
IMSHOW_WIDTH = 320
IMSHOW_HEIGHT = 240
SAVE_INTERVAL = 10 # 每拍10张图片 保存1张

frame_count = 0
saved_frame_count = 0
start_time = time.time()
current_save_interval = 0

camera: cv2.VideoCapture | None = None
camera_settings = (
    (cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG")), # type: ignore
    (cv2.CAP_PROP_FRAME_WIDTH,    640),
    (cv2.CAP_PROP_FRAME_HEIGHT,   480),
    (cv2.CAP_PROP_FPS,             60),
    (cv2.CAP_PROP_AUTO_EXPOSURE,    1), # 手动曝光
    (cv2.CAP_PROP_EXPOSURE,       -64), # 曝光值
)


def init_camera() -> bool:
    """初始化摄像头"""

    global camera
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        logger.error("摄像头 无法打开")
        return False
    
    for prop, value in camera_settings:
        camera.set(prop, value)

    time.sleep(0.5)  # 等待摄像头稳定 

    # 读取测试帧以确认摄像头工作正常
    ret, frame = camera.read()
    if not ret:
        logger.error("摄像头 读取测试帧失败")
        return False
    
    logger.info("摄像头 初始化成功")
    return True


def save_frame(frame: cv2.typing.MatLike) -> None:
    """
    保存拍下的图片

    Args:
        frame (cv2.typing.MatLike): 要保存的图片帧
    
    """

    def worker():
        nonlocal frame

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"img_{timestamp}.png"

        cv2.imwrite(f"{SAVE_PATH}/{filename}", frame)
        logger.info(f"保存: {filename}")
    
    # 判断是否到了保存间隔
    global current_save_interval
    current_save_interval += 1

    if current_save_interval >= SAVE_INTERVAL:
        current_save_interval = 0
        thread = threading.Thread(target=worker)
        thread.start()

def draw_ui(frame: cv2.typing.MatLike) -> cv2.typing.MatLike:
    """
    绘制ui 辅助使用

    Args:
        frame (cv2.typing.MatLike): 摄像头采集的原始帧
    
    Returns:
        cv2.typing.MatLike: 绘制后的图片帧
    """

    global frame_count, saved_frame_count, IMSHOW_WIDTH, IMSHOW_HEIGHT, start_time

    ui_frame = cv2.resize(frame, (IMSHOW_WIDTH, IMSHOW_HEIGHT))
    fps = frame_count / (time.time() - start_time)

    # 帧数显示
    cv2.putText(
        ui_frame,
        f"FPS: {fps:.2f}",
        (5, 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        2
    )

    # 当前已经保存的帧数显示
    cv2.putText(
        ui_frame,
        f"Saved: {saved_frame_count}",
        (5, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        2
    )

    return ui_frame


def main():
    global camera, start_time, frame_count, current_save_interval

    # 创建保存目录 防止不存在导致的保存失败
    os.makedirs(SAVE_PATH, exist_ok=True)

    if not init_camera():
        return

    # 重置计时器
    start_time = time.time()
    
    while True:

        ret, frame = camera.read()

        if not ret:
            logger.error("摄像头 读取帧失败")
            time.sleep(0.1)
            continue

        cv2.imshow("", draw_ui(frame))

        key = cv2.waitKey(5) & 0xFF

        if key == ord('q') or key == ord('Q'):
            # 退出程序
            logger.info("退出中...")
            break
        
        elif key == ord('c') or key == ord('C'):
            # 保存当前帧
            save_frame(frame)

        else:
            pass

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print(r"""
    数据采集工具 v1.0
    按 'C' 键拍照保存当前帧
    按 'Q' 键退出程序
    """)
    main()
