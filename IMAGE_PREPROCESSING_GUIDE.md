# 图像预处理快速指南

## 问题背景
- Raspberry Pi 摄像头无法通过软件调整亮度/曝光
- 画面过曝导致 YOLO 检测精度下降 20-30%

## 解决方案
**多级自适应图像预处理** - 在推理前对图像二次处理

## 快速实施（15 分钟）

### 1. 添加配置到 src/config.py
```python
# ==================== 图像预处理配置 ====================
ENABLE_IMAGE_PREPROCESSING = True
GAMMA_CORRECTION = 1.5
CLAHE_CLIP_LIMIT = 2.5
BRIGHTNESS_THRESHOLD = 160
```

### 2. 修改 src/recognizer.py
在 `_inference_worker()` 中添加预处理调用，在类中添加 `_adaptive_preprocess()` 方法。
详见 `documents/image_preprocessing_strategy.md`

### 3. 测试
```bash
python demo_vision.py
```

## 预期效果
- 检测精度: 65% → 78-85%
- 置信度: 0.5 → 0.7
- 性能损失: 10-20% 帧率

## 详细文档
- 📖 完整分析: `documents/image_preprocessing_strategy.md`
- 🔧 实现指南: 见上述文档中的代码示例
