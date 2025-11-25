#
# training/data_collector.py
#
# @author n1ghts4kura
# @date 2025-11-18
#

import os
import cv2
import time
import threading as t
from datetime import datetime

IF_IMSHOW = True
IMSHOW_WIDTH  = 320
IMSHOW_HEIGHT = 240

PHOTO_SAVE_DIR = "training/data/origin" # directory to save photos

CAMERA_SETTINGS = (
    (cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG")), # type:ignore encoding
    (cv2.CAP_PROP_FRAME_WIDTH,  640), # width
    (cv2.CAP_PROP_FRAME_HEIGHT, 480), # height
    (cv2.CAP_PROP_FPS,           60), # fps
    (cv2.CAP_PROP_AUTO_EXPOSURE,  1), # exposure mode
    (cv2.CAP_PROP_EXPOSURE,     256), # exposure time
)

camera: cv2.VideoCapture | None = None


def init_camera() -> bool:
    """
    初始化摄像头

    Returns:
        是否初始化成功
    """

    print("Start initializing camera...")

    global camera
    if camera:
        print("Camera already initialized.")
        return True # 已经初始化
    
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Cannot open camera. Check wired connection and driver installation.")
        return False
    
    global CAMERA_SETTINGS
    for prop, val in CAMERA_SETTINGS:
        camera.set(prop, val)
    time.sleep(1) # Wait for camera stability.

    actual_width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
    actual_fps = camera.get(cv2.CAP_PROP_FPS)
    actual_fourcc = int(camera.get(cv2.CAP_PROP_FOURCC))
    fourcc_str = "".join([chr((actual_fourcc >> 8 * i) & 0xFF) for i in range(4)])

    print(
        "Camera initialized successfully. "
        f"Resolution: {actual_width}x{actual_height} @ {actual_fps} FPS, "
        f"FOURCC: {fourcc_str}"
    )

    return True


def save_frame(
    frame: cv2.typing.MatLike
) -> None:
    """
    保存当前帧为图片

    Args:
        frame: 当前帧
    """

    def wrapper() -> bool:
        global PHOTO_SAVE_DIR

        if frame is None:
            print("No frame to save.")
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{PHOTO_SAVE_DIR}/img_{timestamp}.jpg"

        try:
            cv2.imwrite(filename, frame)
            print(f"Saved frame to {filename}")
            return True
        except Exception as e:
            print(f"Failed to save frame: {e}")
            return False
    
    thread = t.Thread(target=wrapper)
    thread.start()


def main():
    global camera, PHOTO_SAVE_DIR

    # init camera
    if not init_camera():
        return

    # check used directory existence
    # os.system(f"mkdir {PHOTO_SAVE_DIR}")
    os.makedirs(PHOTO_SAVE_DIR, exist_ok=True)

    frame_count = 0            # 总循环次数（整体 FPS）
    capture_only_count = 0     # 仅采集计数（只读帧）
    save_frame_count = 0
    stats_start_time = time.time()

    while True:
        ok, frame = camera.read()

        if not ok:
            print("failed to read a frame.")
            continue

        # 采集计数（只要成功 read，一次）
        capture_only_count += 1

        if IF_IMSHOW:
            cv2.imshow("", cv2.resize(frame, (IMSHOW_WIDTH, IMSHOW_HEIGHT)))

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == ord('Q'):
            print("Quitting...")
            break
        elif key == ord('c') or key == ord('C'):
            save_frame_count += 1
            if save_frame_count % 12 == 0: # save every 3rd frame
                save_frame(frame) # save current frame
            continue

        end_time = time.time()
        frame_count += 1
        now = time.time()
        elapsed = now - stats_start_time

        if elapsed >= 2.0:  # 每 2 秒打印一次，避免太频繁
            capture_fps = capture_only_count / elapsed
            total_fps = frame_count / elapsed
            print(
                f"Capture FPS (read only): {capture_fps:.2f} | "
                f"Pipeline FPS (with imshow/save): {total_fps:.2f}"
            )
            frame_count = 0
            capture_only_count = 0
            stats_start_time = now
    
    camera.release() # type: ignore
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
