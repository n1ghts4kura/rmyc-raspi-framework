#
# recognizer.py
#
# @author **Aunnno**, n1ghts4kura
# @date 2025-9-10
#

import os
import cv2
from ultralytics import YOLO
import typing as t

IF_PLOT = False # 是否在推理时直接绘制结果

class Recognizer:
    """
    单摄像头、单模型识别器。负责摄像头采集、模型推理、窗口展示。
    用法：
        r = Recognizer()
        r.init_camera()
        r.init_model()
        r.capture()
        r.predict()
        r.clean_up()
    """

    def __init__(
        self,
        cam_width: int = 480,
        cam_height: int = 320,
        cam_fps: float = 60.0,
    ) -> None:
        self.cam_width = cam_width # 摄像头宽度
        self.cam_height = cam_height # 摄像头高度
        self.cam_fps = cam_fps # 摄像头帧率

        # 模型路径
        self.model_path: str = os.getenv("MODEL_PATH", "./model/yolo11n-cls.pt")
        # 模型置信度阈值
        self.conf: float = 0.7
        # 模型IOU阈值
        self.iou: float = 0.7
        # 摄像头对象
        self.cap: t.Optional[cv2.VideoCapture] = None
        # 模型对象
        self.model: t.Optional[YOLO] = None
        # 当前捕获的帧
        self.current_capture_frame: t.Optional[cv2.typing.MatLike] = None
        # 当前标注的帧
        self.current_annotated_frame: t.Optional[cv2.typing.MatLike] = None
        # 当前推理结果
        self.current_results: t.Any = None

    def init_camera(self) -> bool:
        """
        初始化摄像头。
        Returns:
            True 成功, False 失败。
        """

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("摄像头未打开")
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
        self.cap.set(cv2.CAP_PROP_FPS, self.cam_fps)

        ret, _ = self.cap.read()
        if not ret:
            print("摄像头未读取到帧")
            self.cap.release()
            self.cap = None
            return False

        return True

    def init_model(self) -> bool:
        """
        初始化模型。
        Returns:
            True 成功, False 失败。
        """

        try:
            self.model = YOLO(self.model_path)
        except Exception as e:
            print(f"模型加载失败: {e}")
            self.model = None
            return False
        if self.model is None:
            print("模型不存在")
            return False
        return True

    def capture(self) -> bool:
        """
        捕获一帧并保存。
        Returns: True 成功, False 失败。
        """

        if self.cap is None:
            print("摄像头未初始化")
            return False

        ret, frame = self.cap.read()
        if not ret:
            print("未读取到帧")
            return False

        # print(f"Frame captured: {frame.shape}")
        self.current_capture_frame = frame
        return True

    def predict(self) -> bool:
        """
        对当前帧进行推理。
        Returns: True 成功, False 失败。
        """

        if self.current_capture_frame is None:
            print("当前帧为空")
            return False

        if self.model is None:
            print("模型未初始化")
            return False
        
        try:
            self.current_results = self.model.predict(
                source=self.current_capture_frame,
                stream=True,
                conf=self.conf,
                iou=self.iou,
                rect=True,
                # max_det=1,
                # verbose=False,
            )
            self.current_results = tuple(self.current_results)

            return True

        except Exception as e:
            print(f"推理失败: {e}")
            self.current_results = None
            return False

    def annotate(self) -> bool:
        """
        对当前帧进行标注。
        Returns:
            True 成功, False 失败。
        """

        if self.current_capture_frame is None:
            print("当前帧为空")
            return False

        if self.current_results is None:
            print("当前推理结果为空")
            return False

        try:
            frame = self.current_results[0]

            if IF_PLOT:
                frame = frame.plot(
                    # args:
                    conf=False,
                    masks=False,
                    probs=False,

                )
            else:
                frame = frame.orig_img

            self.current_annotated_frame = frame
            return True

        except Exception as e:
            print(f"标注失败: {e}")
            self.current_annotated_frame = None
            return False

    def imshow(self) -> None:
        """显示当前帧和推理结果"""

        if self.current_annotated_frame is None:
            print("当前帧为空")
            return

        cv2.imshow("Recognizer", self.current_annotated_frame)
        cv2.waitKey(1)

    def clean_up(self) -> None:
        """释放摄像头和窗口资源"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

        cv2.destroyAllWindows()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean_up()
