# 下一步行动指南

**当前状态**: ✅ 图像预处理系统开发完成  
**日期**: 2025-10-12

---

## 🎯 立即行动（今天完成）

### 1. 验证预处理功能 ⭐ **最重要**

#### 测试数据采集
```bash
# 启动数据采集工具
python training/data_collector.py
```

**验证要点**:
- [ ] 预览窗口显示的图像是否比原始图像更亮（gamma=1.3 效果）
- [ ] 按 `c` 拍照，保存的图像是否应用了预处理
- [ ] 按 `v` 录像，录制的视频是否应用了预处理
- [ ] 检查 `training/photos/` 和 `training/videos/` 中的文件

#### 测试实时预测
```bash
# 运行视觉识别 demo
python demo_vision.py
```

**验证要点**:
- [ ] 检查终端输出，确认预处理已启用
- [ ] 观察检测效果，与未预处理时对比

---

## 📋 短期任务（1-3天）

### 2. 数据采集准备

#### 场景规划
根据比赛场地，需要采集以下场景的数据：

| 场景类型 | 光照条件 | 采集数量 | 优先级 |
|---------|---------|---------|-------|
| **正常光照** | 室内正常灯光 | 200+ 张 | ⭐⭐⭐ |
| **强光** | 靠近窗户/室外 | 100+ 张 | ⭐⭐ |
| **弱光** | 阴影/昏暗区域 | 100+ 张 | ⭐⭐ |
| **混合光** | 不同光源混合 | 50+ 张 | ⭐ |

#### 数据质量要求
- ✅ 目标装甲板清晰可见
- ✅ 多角度（正面、侧面、倾斜）
- ✅ 多距离（近、中、远）
- ✅ 包含干扰物（其他机器人、背景）

#### 采集命令
```bash
# 1. 启动数据采集
python training/data_collector.py

# 2. 调整焦距（如需要）
#    - 按 +/- 调整
#    - 找到最清晰的焦距值

# 3. 开始采集
#    - 按 'c' 拍照
#    - 按 'v' 开始/停止录像
#    - 按 'q' 退出

# 4. 数据保存在
#    training/photos/
#    training/videos/
```

---

## 🔧 中期任务（3-7天）

### 3. 参数调优（可选）

如果发现当前 gamma=1.3 效果不理想：

#### 调优步骤
```bash
# 1. 修改配置
vim src/config.py
# 修改 IMAGE_PREPROCESSING_GAMMA 值

# 2. 重新采集数据（关键！）
python training/data_collector.py

# 3. 测试新参数效果
python demo_vision.py
```

#### 参数建议
```python
# 场景过亮
IMAGE_PREPROCESSING_GAMMA = 0.9  # 压暗

# 场景正常
IMAGE_PREPROCESSING_GAMMA = 1.3  # 当前值

# 场景过暗
IMAGE_PREPROCESSING_GAMMA = 1.8  # 提亮
```

### 4. YOLO 模型训练

#### 训练准备
```bash
# 1. 标注数据
#    使用 LabelImg 或 Roboflow 标注采集的图像

# 2. 准备数据集
#    - 训练集：70%
#    - 验证集：20%
#    - 测试集：10%

# 3. 配置 YOLO
#    - 修改 data.yaml
#    - 设置类别（如：red_armor, blue_armor）
```

#### 训练命令（示例）
```python
from ultralytics import YOLO

# 加载预训练模型
model = YOLO('yolov8n.pt')

# 训练
model.train(
    data='path/to/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    device='cpu'  # 树莓派用 CPU
)
```

---

## 🚀 长期任务（1-2周）

### 5. 系统集成测试

#### 完整流程测试
```bash
# 1. 启动主程序
python src/main.py

# 2. 测试功能
#    - 按键触发技能
#    - 检查串口通信
#    - 验证硬件控制

# 3. 性能监控
#    - FPS 是否 >20
#    - CPU 占用率
#    - 内存使用情况
```

### 6. 性能优化（如需要）

#### 优化方向
- [ ] 降低模型复杂度（YOLOv8n → YOLOv8n-lite）
- [ ] 减小图像分辨率（640x480 → 480x320）
- [ ] 优化预处理性能（已使用 LUT，无需优化）
- [ ] 多线程优化（视觉、控制、通信分离）

---

## ⚠️ 关键注意事项

### 必须记住！
1. **修改 gamma 值 = 必须重新采集数据**
2. **训练数据预处理 = 预测时预处理**（已保证）
3. **所有参数通过 `config.py` 管理**（已实现）

### 常见问题快速排查

| 问题 | 检查项 | 解决方案 |
|------|--------|---------|
| 预处理未生效 | `config.ENABLE_IMAGE_PREPROCESSING` | 确保为 `True` |
| 图像太亮/太暗 | `config.IMAGE_PREPROCESSING_GAMMA` | 调整数值并重新采集数据 |
| 导入错误 | `from utils import adjust_gamma` | 检查 Python 路径 |
| 训练效果差 | 数据质量、预处理一致性 | 重新采集高质量数据 |

---

## 📚 参考文档

| 文档 | 用途 |
|------|------|
| `documents/task_completion_summary.md` | 任务完成总结 |
| `documents/checklist_image_preprocessing.md` | 完成度检查清单 |
| `documents/image_preprocessing_implementation.md` | 实施方案 |
| `training/README.md` | 数据采集工具使用说明 |

---

## 🎯 当前优先级排序

1. ⭐⭐⭐ **验证预处理功能**（今天完成）
2. ⭐⭐⭐ **采集训练数据**（3天内完成）
3. ⭐⭐ **数据标注**（5天内完成）
4. ⭐⭐ **YOLO 训练**（1周内完成）
5. ⭐ **系统集成测试**（2周内完成）

---

**建议**: 先完成 #1 验证功能，确认预处理正常工作后再进行数据采集。

**记录**: 所有测试结果和问题请记录，便于后续优化。
