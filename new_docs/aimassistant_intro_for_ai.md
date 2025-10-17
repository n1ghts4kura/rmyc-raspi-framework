# 自瞄系统 (Aim Assistant) - AI 技术文档

## 概述

**目标**: 为 RoboMaster EP 步兵机器人提供自动瞄准能力

**硬件**: 树莓派 4B + USB 摄像头 + 串口连接云台

**版本**: v1.0 (简化实现方案)

**性能指标**:
- 控制频率: 20 Hz
- 推理帧率: 4.15 FPS
- 目标丢失容忍: 12 帧 (~3秒)

---

## 系统架构

```
USB 摄像头 → YOLO 检测 (recognizer.py)
    ↓
目标选择 (selector.py) - 评分排序
    ↓
角度解算 (angle.py) - 像素坐标 → 云台角度
    ↓
云台控制 (gimbal.py) - 串口指令下发
```

---

## 核心模块

### 1. 目标选择器 (`src/aimassistant/selector.py`)

**功能**: 从多个检测目标中选择最优目标

**评分算法**:
```python
score = area_factor * 0.5 + center_factor * 0.3 + confidence_factor * 0.2
```

**权重设计**:
- 面积因子: 0.5 (主要) - 近距离目标优先
- 中心因子: 0.3 (次要) - 画面中心优先
- 置信度: 0.2 (辅助) - 高置信度优先

### 2. 角度解算器 (`src/aimassistant/angle.py`)

**功能**: 将像素坐标转换为云台角度

**核心公式** (针孔相机模型):
```python
# 归一化坐标
xn = bbox_center_x / img_width
yn = bbox_center_y / img_height

# 计算垂直 FOV
fov_vertical = fov_horizontal * (img_height / img_width)

# 角度转换
yaw = (xn - 0.5) * fov_horizontal
pitch = -(yn - 0.5) * fov_vertical
```

**关键参数**: `CAMERA_FOV_HORIZONTAL = 70°` (⚠️ 需硬件校准)

### 3. 自瞄管线 (`src/aimassistant/pipeline.py`)

**主函数**: `aim_step_v1(recognizer, gimbal_speed)`

**执行流程**:
1. 获取 YOLO 检测结果
2. 选择最优目标
3. 解算云台角度
4. 下发控制指令

### 4. 自瞄技能 (`src/skill/auto_aim_skill.py`)

**绑定按键**: 'z'

**目标丢失处理**:
- 容忍短时丢失 (< 12 帧)
- 长时间丢失 → 云台回中

---

## 配置参数 (`src/config.py`)

```python
# 自瞄系统
CAMERA_FOV_HORIZONTAL = 70.0              # ⚠️ 需校准
GIMBAL_SPEED = 90                         # ⚠️ 需调优
AIM_LOST_TARGET_TIMEOUT_FRAMES = 12
AIM_CONTROL_FREQUENCY = 20
```

---

## 与原设计的差异

**简化方案 A** (当前实现):
- ✅ 使用面积因子替代单目测距
- ✅ 使用机器人固件控制替代 PID
- ✅ 固定频率替代自适应管理
- ✅ Python 字典配置替代 YAML

**详细历程**: `archive/aimassistant_implementation_journey.md`

---

## 已知限制

1. **无精确测距**: 使用面积因子近似
2. **无 PID 控制**: 依赖机器人固件
3. **参数需校准**: FOV 和云台速度为估算值

---

## 相关文档

- 项目总览: `general_intro_for_ai.md`
- 实现历程: `archive/aimassistant_implementation_journey.md`
- 云台控制: `archive/gimbal_360_implementation_journey.md`

---

**最后更新**: 2025-10-13  
**状态**: ✅ 代码完成,等待硬件测试
