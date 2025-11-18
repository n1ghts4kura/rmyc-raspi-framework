#
# training/data_collector_v2.py
#
# @author n1ghts4kura
# @date 2025-11-18
#

import cv2
import time

CAMERA_SETTINGS = (
    (cv2.CAP_PROP_FRAME_WIDTH,  640), # width
    (cv2.CAP_PROP_FRAME_HEIGHT, 480), # height
    (cv2.CAP_PROP_FPS,          60),  # fps
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
    print("Camera initialized successfully. Resolution: " \
          f"{actual_width}x{actual_height}@{actual_fps}fps"
    )

    return True

def main():
    
    init_camera()

if __name__ == "__main__":
    main()
