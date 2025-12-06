# gimbal.py
# 装甲板检测器
#
# @author n1ghts4kura
# @date 25-12-6
#

import cv2
from dataclasses import dataclass
from ultralytics import YOLO
from ultralytics.engine.results import Results


from src import config
from src import logger


@dataclass
class GimbalDetectionResult:
    """
    装甲板检测结果数据类
    """
    cls_id: int               # 目标类别ID 1 - 红色装甲板 2 - 蓝色装甲板
    confidence: float         # 目标置信度
    xywh: tuple[float, float, float, float]  # 目标边界框 (x_center, y_center, width, height)


class GimbalDetector:
    """
    装甲板检测器
    """

    def __init__(self):
        self.model: YOLO | None = None


    def initialize(self) -> bool:
        """
        初始化检测器

        Returns:
            bool: 初始化是否成功
        """

        try:
            self.model = YOLO(config.AIMBOT_MODEL_PATH)
            return True
        except Exception as e:
            logger.error(f"装甲板检测器初始化失败: {e}")
            return False
    
    
    def detect(self, frame: cv2.typing.MatLike) -> list[GimbalDetectionResult]:
        """
        在给定帧中检测装甲板

        Args:
            frame (cv2.typing.MatLike): 输入图像帧

        Returns:
            list[GimbalDetectionResult]: 检测到的装甲板列表
        """

        if self.model is None:
            logger.error("装甲板检测器未初始化")
            return []

        results_list: list[GimbalDetectionResult] = []

        # 强制只读取第一个result (可能会发生意外 但是不太可能)
        result = self.model.predict(frame, verbose=False, device=config.AIMBOT_PREDICT_DEVICE)[0]
        result = result.cpu()  # 确保在CPU上处理

        # 如果没有检测到任何目标，返回空列表
        if result.boxes is None:
            return []

        # 解析检测结果
        for box in result.boxes: 
            cls_id = int(box.cls[0]) # 类别ID
            confidence = float(box.conf[0]) # 置信度
            # 边界框坐标 (x_center, y_center, width, height)
            x_center, y_center, width, height = box.xywh[0].tolist()

            detection_result = GimbalDetectionResult(
                cls_id=cls_id,
                confidence=confidence,
                xywh=(x_center, y_center, width, height)
            )
            results_list.append(detection_result)

        return results_list
