# Utils 工具模块技术文档

## 📋 模块概述

**文件**: `src/utils.py`  
**作者**: n1ghts4kura  
**创建日期**: 2025-10-12  
**用途**: 提供项目通用的工具函数

---

## 🔧 核心功能

### 1. 图像预处理

#### `adjust_gamma()` - Gamma 校正

**函数签名**:
```python
def adjust_gamma(frame: np.ndarray, gamma: float = 1.0) -> np.ndarray
```

**功能描述**:  
对输入图像应用 Gamma 校正，用于调整图像亮度

**参数**:
- `frame` (np.ndarray): 输入图像（BGR 或灰度）
- `gamma` (float, 默认=1.0): Gamma 值
  - `gamma > 1.0`: 提亮暗部（适合欠曝场景）
  - `gamma < 1.0`: 压暗高光（适合过曝场景）
  - `gamma = 1.0`: 无变化

**返回值**:
- `np.ndarray`: 校正后的图像

**算法原理**:
```python
Output = (Input / 255) ^ (1/gamma) * 255
```

通过查找表（LUT）实现快速计算

**使用场景**:
1. **数据采集预处理** (`training/data_collector.py`)
   - 统一训练数据的亮度分布
   - 补偿摄像头自动曝光不足

2. **实时预测预处理** (`src/recognizer.py`)
   - 确保预测输入与训练数据一致
   - 提高模型泛化能力

**使用示例**:
```python
from utils import adjust_gamma

# 提亮图像
brightened = adjust_gamma(frame, gamma=1.3)

# 压暗图像
darkened = adjust_gamma(frame, gamma=0.8)

# 与配置系统集成
import config
if config.ENABLE_IMAGE_PREPROCESSING:
    frame = adjust_gamma(frame, config.IMAGE_PREPROCESSING_GAMMA)
```

---

## 📊 模块依赖

### 导入的库
```python
import cv2          # OpenCV 图像处理
import numpy as np  # 数值计算
```

### 被导入的模块
- `src/recognizer.py` - 实时预测预处理
- `training/data_collector.py` - 数据采集预处理

---

## 🔄 版本历史

### v1.0 (2025-10-12)
- 创建 `adjust_gamma()` 函数
- 添加类型提示和文档注释
- 集成到预处理流程

---

## ⚠️ 注意事项

### 1. 训练-预测一致性
确保数据采集和预测使用**相同的 gamma 值**：

```python
# ❌ 错误：不同的 gamma 值
# 数据采集
frame = adjust_gamma(frame, gamma=1.3)

# 预测
frame = adjust_gamma(frame, gamma=1.5)  # 不一致！

# ✅ 正确：统一使用配置
import config
frame = adjust_gamma(frame, config.IMAGE_PREPROCESSING_GAMMA)
```

### 2. 性能考虑
- 使用 LUT (Look-Up Table) 实现，时间复杂度 O(1)
- 适用于实时处理（20+ FPS）
- 可在主循环中频繁调用

### 3. 参数范围
- 推荐范围: `0.5 <= gamma <= 2.0`
- 超出范围可能导致图像失真
- 需根据实际场景调优

---

## 🚀 扩展方向

### 未来可添加的工具函数

1. **直方图均衡化**:
   ```python
   def histogram_equalization(frame: np.ndarray) -> np.ndarray:
       """CLAHE 或全局直方图均衡"""
   ```

2. **色彩空间转换**:
   ```python
   def convert_colorspace(frame: np.ndarray, mode: str) -> np.ndarray:
       """BGR → RGB/HSV/LAB/YUV"""
   ```

3. **图像降噪**:
   ```python
   def denoise(frame: np.ndarray, method: str = 'bilateral') -> np.ndarray:
       """双边滤波/非局部均值降噪"""
   ```

4. **图像锐化**:
   ```python
   def sharpen(frame: np.ndarray, strength: float = 1.0) -> np.ndarray:
       """USM锐化/拉普拉斯锐化"""
   ```

---

## 📚 相关文档

- `documents/image_preprocessing_implementation.md` - 预处理实施方案
- `documents/image_preprocessing_strategy.md` - 技术分析
- `src/config.py` - 配置管理
- `documents/coding_style_guide_for_ai.md` - 编码规范

---

**维护**: RMYC Framework Team  
**最后更新**: 2025-10-12
