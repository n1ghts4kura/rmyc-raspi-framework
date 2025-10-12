#
# utils.py
#
# @author n1ghts4kura
# @date 2025/10/12
#


import cv2
import numpy as np
from functools import lru_cache


@lru_cache(maxsize=32)
def _create_gamma_lut(gamma: float) -> np.ndarray:
    """
    创建并缓存 Gamma 校正查找表（LUT）
    
    Args:
        gamma: Gamma值
    
    Returns:
        查找表（256 个元素）
    """
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 
                      for i in np.arange(0, 256)]).astype("uint8")
    return table


def adjust_gamma(frame: np.ndarray, gamma: float = 1.0) -> np.ndarray:
    """
    Gamma校正预处理（使用缓存的 LUT 表优化性能）
    
    Args:
        frame: 输入图像
        gamma: Gamma值 (>1 提亮暗部, <1 压暗高光)
    
    Returns:
        校正后的图像
    
    性能优化:
        - LUT 表使用 lru_cache 缓存，避免重复计算
        - 相同 gamma 值只计算一次
        - 查找时间复杂度 O(1)
    """
    if gamma == 1.0:
        return frame  # gamma=1.0 时无需处理
    
    table = _create_gamma_lut(gamma)
    return cv2.LUT(frame, table)
