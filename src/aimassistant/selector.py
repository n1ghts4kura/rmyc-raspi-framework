#
# aimassistant/selector.py
# 目标选择器
# 用于在多个检测目标中选择最优目标
#
# @author n1ghts4kura
# @date 2025/10/2
#

import math
from functools import wraps
from ultralytics.engine.results import Boxes

_weight_sum = 0.0
def weight_setting(weight: float):
    """
    权重设置装饰器
    
    Args:
        weight (float): 该选择器的权重，范围为 0.0 到 1.0，且所有选择器的权重总和不能超过 1.0。
    Raises:
        ValueError: 如果权重总和超过 1.0，则抛出异常。
    """

    global _weight_sum
    _weight_sum += weight
    if _weight_sum > 1.0:
        raise ValueError("权重总和不能超过 1.0")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs) * weight
        return wrapper
    return decorator


# ========= v1 =========
v1_weight = 10.0 # 总权重 这个值越大 对于细微的差异越敏感


@weight_setting(0.45)
def box_square_factor_v1(box: Boxes) -> float:
    """
    检测框面积 因子 v1 - 面积越大，离目标越近

    Args:
        box (Boxes): **单个** 目标边界框
    Returns:
        float: 检测框面积 因子，范围 [0.0, 1.0]
    """

    _, _, w, h = box.xywhn[0]
    return float(w) * float(h)


@weight_setting(0.2)
def box_center_factor_v1(box: Boxes) -> float:
    """
    检测框中心点 因子 v1 - 中心点越接近画面中心，离目标越近

    Args:
        box (Boxes): **单个** 目标边界框
    Returns:
        float: 检测框中心点 因子，范围 [0.0, 1.0]
    """

    x, y, _, _ = box.xywhn[0]
    distance = math.sqrt(x ** 2 + y ** 2)
    max_distance = 0.7071067811865476  # 对角线距离
    return max(0.0, 1.0 - distance / max_distance) # => [0.0, 1.0]


@weight_setting(0.35)
def confidence_factor_v1(box: Boxes) -> float:
    """
    置信度 因子 v1 - 置信度越高，离目标越近

    Args:
        box (Boxes): **单个** 目标边界框
    Returns:
        float: 置信度 因子，范围 [0.0, 1.0]
    """

    return float(box.conf[0])


def selector_v1(boxes: Boxes) -> Boxes:
    """
    目标选择器 v1 - 综合考虑面积、中心点和置信度

    Args:
        boxes (Boxes): 多个目标边界框
    Returns:
        Boxes: 选择的最优目标边界框
    """

    best_box = boxes[0]
    best_score = -1.0

    for box in boxes:
        score = (
            box_square_factor_v1(box) +
            box_center_factor_v1(box) +
            confidence_factor_v1(box)
        ) * v1_weight
        if score > best_score:
            best_score = score
            best_box = box

    return best_box

