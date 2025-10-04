#
# aimassistant/angle.py
# 角度解算模块
# 计算云台瞄准目标所需的偏航角和俯仰角
#
# @author n1ghts4kura
# @date 2025/10/3
#


import math
import config
from ultralytics.engine.results import Boxes


def calculate_angles(box: Boxes) -> tuple[float, float]:
    """
    将 YOLO 检测框的归一化坐标转换为云台偏航角和俯仰角。
    
    Args:
        box (Boxes): YOLO 检测结果的单个 Boxes 对象
    Returns:
        tuple[float, float]: (yaw, pitch) 云台控制角度（单位：度）
    Example:
        >>> yaw, pitch = calculate_angles(box) # yaw为水平偏航角，pitch为垂直俯仰角
    """

    # 获取归一化的中心坐标（符合 YOLO xywhn 格式）
    center_x_n, center_y_n, _, _ = box.xywhn[0]
    
    # 计算相对于图像中心（0.5, 0.5）的归一化偏移量
    dx_norm = float(center_x_n) - 0.5  # 水平偏移
    dy_norm = float(center_y_n) - 0.5  # 垂直偏移
    
    # 根据针孔相机模型，垂直 FOV 由水平 FOV 和长宽比决定
    # FOV_V = 2 * arctan(tan(FOV_H/2) * height/width)
    fov_h_rad = math.radians(config.CAMERA_FOV_HORIZONTAL)
    aspect_ratio = config.CAMERA_HEIGHT / config.CAMERA_WIDTH
    fov_v_rad = 2 * math.atan(math.tan(fov_h_rad / 2) * aspect_ratio)
    fov_v_deg = math.degrees(fov_v_rad)
    
    # 将归一化偏移量转换为云台控制角度
    yaw = dx_norm * config.CAMERA_FOV_HORIZONTAL
    pitch = -dy_norm * fov_v_deg
    
    return yaw, pitch
