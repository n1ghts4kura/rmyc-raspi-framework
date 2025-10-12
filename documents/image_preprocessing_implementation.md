# 图像预处理实施方案

## 📋 背景

**日期**: 2025-10-12  
**问题**: 树莓派摄像头不支持硬件曝光控制，导致不同场景亮度差异影响YOLO模型训练和预测  
**解决方案**: 使用软件 Gamma 校正归一化亮度

---

## ⚠️ 关键原则

> **训练看到什么，预测就必须看到什么**
> 
> 任何预处理（硬件/软件）必须在训练和预测时**完全一致**

---

## 🔧 实施细节

### 1. 硬件能力验证

运行测试发现：
```bash
v4l2-ctl -d /dev/video0 --list-ctrls
```

**结果**: 树莓派摄像头**不支持**以下参数：
- ❌ `cv2.CAP_PROP_AUTO_EXPOSURE` (手动曝光模式)
- ❌ `cv2.CAP_PROP_EXPOSURE` (曝光值设置)
- ❌ `cv2.CAP_PROP_BRIGHTNESS` (亮度控制)

**结论**: 必须使用软件预处理方案

---

### 2. 配置参数（`src/config.py`）

添加以下配置：

```python
# ============================================================
# 图像预处理配置
# ============================================================
# ⚠️ 关键：训练数据采集时的预处理参数必须与预测时完全一致！

# 是否启用图像预处理（数据采集和预测时都生效）
ENABLE_IMAGE_PREPROCESSING = True

# Gamma 校正值
# - gamma > 1.0: 提亮暗部（适合过曝场景）
# - gamma < 1.0: 压暗高光（适合欠曝场景）
# - gamma = 1.0: 无变化
IMAGE_PREPROCESSING_GAMMA = 1.3
```

---

### 3. Gamma 校正函数

```python
def adjust_gamma(image: np.ndarray, gamma: float = 1.0) -> np.ndarray:
    """
    Gamma校正预处理
    
    Args:
        image: 输入图像
        gamma: Gamma值 (>1 提亮暗部, <1 压暗高光)
    
    Returns:
        校正后的图像
    """
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)
```

---

### 4. 数据采集（`training/data_collector.py`）

**修改内容**：
1. 导入 `config` 模块
2. 从配置读取 `gamma` 参数
3. 对所有捕获帧应用 Gamma 校正

**关键代码**：
```python
# 导入配置
import config

class DataCollector:
    def __init__(self, ..., gamma: float = None):
        # 从配置文件读取 gamma 值（如果未指定）
        if gamma is None:
            gamma = config.IMAGE_PREPROCESSING_GAMMA if config.ENABLE_IMAGE_PREPROCESSING else 1.0
        self.gamma = gamma
    
    def run(self):
        while self.is_running:
            ret, frame = self.cap.read()
            
            # 对所有捕获的帧应用 Gamma 校正预处理
            frame = self._apply_preprocessing(frame)
            
            # ... 录像、显示等
```

---

### 5. 实时预测（`src/recognizer.py`）

**修改内容**：
1. 添加 `adjust_gamma()` 函数（与 data_collector.py 相同）
2. 在 YOLO 推理前应用相同的预处理

**关键代码**：
```python
def _process_frame(self, frame):
    """处理单帧：推理 + 生成注释帧 + 更新结果"""
    try:
        # 应用与训练一致的图像预处理（关键！）
        if config.ENABLE_IMAGE_PREPROCESSING:
            frame = adjust_gamma(frame, config.IMAGE_PREPROCESSING_GAMMA)
        
        # 执行推理
        results = self.model.predict(
            source=frame,
            conf=self.conf,
            iou=self.iou,
            verbose=False
        )
        # ...
```

---

## 📊 一致性保证

### 训练流程
1. **数据采集**: `training/data_collector.py`
   - 启用预处理: `ENABLE_IMAGE_PREPROCESSING = True`
   - Gamma 值: `IMAGE_PREPROCESSING_GAMMA = 1.3`
   - 所有捕获帧应用 Gamma 校正
   - 保存预处理后的图像/视频

2. **模型训练**: 
   - 使用预处理后的数据训练 YOLO 模型
   - 模型学习的是"Gamma=1.3"后的图像分布

### 预测流程
1. **实时预测**: `src/recognizer.py`
   - 启用预处理: `config.ENABLE_IMAGE_PREPROCESSING = True`
   - Gamma 值: `config.IMAGE_PREPROCESSING_GAMMA = 1.3`
   - 推理前对每帧应用相同 Gamma 校正
   - 确保输入分布与训练时一致

---

## ✅ 验证清单

使用前请确认：

- [ ] `src/config.py` 中的 `IMAGE_PREPROCESSING_GAMMA` 值已设置
- [ ] `training/data_collector.py` 从 `config.py` 读取 gamma 参数
- [ ] `src/recognizer.py` 在推理前应用相同的 gamma 处理
- [ ] 已有训练数据的预处理参数已记录
- [ ] 如果修改 gamma 值，需重新采集所有训练数据

---

## 🚨 常见错误

### 错误1: 训练-预测不一致
**症状**: 训练精度高，实际预测效果差  
**原因**: 训练数据应用了预处理，但预测时未应用  
**解决**: 确保 `recognizer.py` 中的预处理逻辑已启用

### 错误2: 参数不匹配
**症状**: 预测结果不稳定  
**原因**: 采集时 gamma=1.3，预测时 gamma=1.5  
**解决**: 统一使用 `config.IMAGE_PREPROCESSING_GAMMA`

### 错误3: 忘记更新配置
**症状**: 修改了 `data_collector.py` 的 gamma，但预测未生效  
**原因**: 忘记更新 `config.py`  
**解决**: 始终通过 `config.py` 管理参数

---

## 📝 参数调优指南

### 当前设置
- **Gamma = 1.3**: 轻度提亮，补偿摄像头自动曝光不足

### 调优建议
1. **过曝场景** (平均亮度 > 180):
   - 降低 gamma 值 (0.8 - 1.0)
   - 压暗高光区域

2. **欠曝场景** (平均亮度 < 80):
   - 提高 gamma 值 (1.5 - 2.0)
   - 提亮暗部区域

3. **正常场景** (平均亮度 100-180):
   - 保持 gamma = 1.0 - 1.3
   - 轻度增强即可

### 修改流程
1. 修改 `src/config.py` 中的 `IMAGE_PREPROCESSING_GAMMA`
2. **重新采集所有训练数据**
3. 重新训练 YOLO 模型
4. 预测时自动使用新的 gamma 值（从配置读取）

---

## 📚 相关文档

- `documents/image_preprocessing_strategy.md` - 详细技术方案
- `documents/image_preprocessing_guide.md` - 快速实施指南
- `test_camera_controls.py` - 硬件能力测试脚本

---

## 🎯 总结

✅ **实施完成**:
1. 硬件能力测试：确认不支持手动曝光
2. 配置管理：在 `config.py` 中统一管理预处理参数
3. 数据采集：`data_collector.py` 对所有帧应用 Gamma 校正
4. 实时预测：`recognizer.py` 应用相同的预处理
5. 一致性保证：训练和预测使用完全相同的参数

⚠️ **关键要点**:
- 修改 gamma 值 = 需要重新采集数据
- 训练数据预处理 = 预测时预处理
- 所有参数通过 `config.py` 统一管理

🚀 **下一步**:
1. 采集足够的训练数据（各种光照场景）
2. 训练 YOLO 模型
3. 实测预测效果
4. 根据结果调优 gamma 值

---

**维护**: RMYC Framework Team  
**最后更新**: 2025-10-12
