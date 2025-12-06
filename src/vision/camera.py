# camera.py
# 摄像头管理类
#
# @author n1ghts4kura
# @date 25-12-5
#

import cv2
import time
import threading

from src import config

class Camera:
    """
    摄像头
    单例类
    统一管理摄像头资源
    """

    # 单例类设计
    _instance: 'Camera | None' = None
    _instance_lock = threading.Lock() # 线程锁 防止多个线程同时访问该类造成问题

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._instance_lock:
                if not cls._instance:
                    cls._instance = super(Camera, cls).__new__(cls)
        return cls._instance

    
    def __init__(self):
        self._cap: cv2.VideoCapture | None = None
        self._is_opened: bool = False
    
    def open(self) -> bool:
        """
        打开摄像头
        """
        if self._is_opened:
            return True
        
        self._cap = cv2.VideoCapture(config.CAMERA_INDEX)

        if not self._cap.isOpened():
            return False
        
        # 设置摄像头参数
        self._cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*config.CAMERA_FOURCC)) # type:ignore encoding
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH,  config.CAMERA_WIDTH)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        self._cap.set(cv2.CAP_PROP_FPS,          config.CAMERA_FPS)
        self._cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, config.CAMERA_AUTO_EXPOSURE)
        self._cap.set(cv2.CAP_PROP_EXPOSURE,     config.CAMERA_EXPOSURE)
        # 等待摄像头稳定
        time.sleep(0.5)

        self._is_opened = True
        return True
    
    def test_opened(self) -> bool:
        """
        从摄像头读取一帧测试是否打开成功

        Returns:
            是否打开成功
        """

        if not self._is_opened or not self._cap:
            return False
        
        ret, _ = self._cap.read()
        return ret
    
    def read(self) -> tuple[bool, cv2.typing.MatLike | None]:
        """
        读取一帧图像

        Returns:
            读取到的图像，读取失败返回None
        """

        if not self._is_opened or not self._cap:
            return False, None
        
        ret, frame = self._cap.read()
        return ret, frame
    
    def close(self) -> None:
        """
        关闭摄像头
        """

        if not self._is_opened or not self._cap:
            return
        
        self._cap.release()
        self._is_opened = False
    
    def get_actual_settings(self) -> dict | None:
        """
        获取摄像头实际参数

        Returns:
            width: 实际宽度
            height: 实际高度
            fps: 实际帧率
            fourcc: 实际编码格式
        """

        if not self._is_opened or not self._cap:
            return None
        
        actual_width = self._cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        actual_fps = self._cap.get(cv2.CAP_PROP_FPS)
        actual_fourcc = int(self._cap.get(cv2.CAP_PROP_FOURCC))
        fourcc_str = "".join([chr((actual_fourcc >> 8 * i) & 0xFF) for i in range(4)])

        return {
            "width": actual_width,
            "height": actual_height,
            "fps": actual_fps,
            "fourcc": fourcc_str,
        }
    
    def __str__(self) -> str:
        actual_settings = self.get_actual_settings()

        if not actual_settings:
            return "Camera(not opened)"
        
        return (
            "Camera("
            f"{actual_settings['width']}x{actual_settings['height']}@"
            f"{actual_settings['fps']}FPS, "
            f"fourcc: {actual_settings['fourcc']}"
            ")"
        )
