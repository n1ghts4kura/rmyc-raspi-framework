---
title: Aim Assistant 模块 Legacy 概览
version: 2025-10-18
status: archive
maintainers:
    - Copilot Assistant
category: history
last_updated: 2025-10-18
related_docs:
    - new_docs/general_intro_for_ai.md
    - documents/history/aimassistant_implementation_history.md
    - documents/guide/PERFORMANCE_OPTIMIZATION_SUMMARY.md
llm_prompts:
    - "参考旧版自瞄设计，评估当前实现差异"
---

# Aim Assistant 模块面向 AI 协作指南（Legacy）

> **说明**：本文件保留旧版设计提案，包含尚未实现的模块（如 PID 控制、单目测距、AdaptivePerformanceManager）。请在阅读后与 `documents/history/aimassistant_implementation_history.md` 对照，识别实际落地范围，并在新文档中注明差异。

## 背景与目标

- **项目定位**：在 RMYC Raspi Framework 内构建实时自瞄子系统，服务于 RoboMaster EP 步兵机器人自动阶段的精准打击需求。
- **硬件基础**：树莓派 4B 作为上位机，外接 USB 摄像头，串口连接 RoboMaster EP 云台与发射机构。
- **设计初衷**：结合 YOLOv8n 检测、单目测距与姿态求解，提供稳定的目标锁定与自适应性能管理能力。
- **目标成果**：在 15–25 FPS 的算力预算内实现 ≥40% 命中率，并与框架现有技能管理、串口通讯模块深度集成。

## 系统架构概览

```text
树莓派 4B (主控)
    ├── USB 摄像头 → Frame Grabber
    ├── YOLOv8n 目标检测 (装甲板识别)
    ├── Omega 评分器 (多目标选择)
    ├── 单目测距 + 偏航/俯仰角解算
    ├── Adaptive Performance Manager (自适应性能调度)
    └── UART 指令下发 → RoboMaster EP (云台 / 发射机构)
```

## 模块拆分与职责

- **摄像头采集层**：控制 USB 摄像头分辨率、帧率、曝光等；提供校准接口。
- **YOLO 检测器**：在 640×640 输入下输出边界框、类别与置信度；支持 FP16 推理、帧率自适应。
- **候选筛选器**：过滤低置信、尺寸异常、画面边缘目标；维护历史轨迹。
- **MonocularDistanceEstimator**：基于相似三角形估算射程，提供校准与估算接口。
- **Angle Solver**：使用相机内参换算偏航角、俯仰角。
- **Omega 评分系统**：依据距离因子 + 角度因子为多目标排名，权重随性能模式动态调整。
- **AdaptivePerformanceManager**：根据实时 FPS、目标数量、战术压力切换 fast / balanced / precise 三档策略。
- **Control Output**：使用 PID 平滑角度指令，通过 `bot.conn` 串口发送 `"YAW:xx,PITCH:yy"` 格式命令。
- **异常处理**：目标丢失时预测或进入扫描模式；串口异常时重试并进入安全态。

建议在 `src/model/` 中新增 `aimassistant/` 子包，按上述职责拆分文件（例如 `detector.py`、`distance.py`、`angle.py`、`selector.py`、`adaptive.py`、`controller.py`、`pipeline.py`）。

## 核心算法速览

### 单目测距

```python
class MonocularDistanceEstimator:
    def __init__(self, real_width=0.13, real_height=0.05):
        self.real_width = real_width
        self.real_height = real_height
        self.focal_length = None

    def calibrate(self, known_distance, pixel_width, pixel_height):
        focal_x = (pixel_width * known_distance) / self.real_width
        focal_y = (pixel_height * known_distance) / self.real_height
        self.focal_length = (focal_x + focal_y) / 2

    def estimate(self, pixel_width, pixel_height):
        distance_w = (self.real_width * self.focal_length) / pixel_width
        distance_h = (self.real_height * self.focal_length) / pixel_height
        return (distance_w + distance_h) / 2
```

### 角度解算

- 偏航角：$\arctan (\Delta x / f_x)$
- 俯仰角：$\arctan (\Delta y / f_y)$

### Omega 评分

```python
def distance_factor(actual_distance, min_dist=1.0, max_dist=8.0, decay=0.5):
    clamped = max(min_dist, min(actual_distance, max_dist))
    return math.exp(-decay * (clamped - min_dist))


def angle_factor(bbox, image_center, target_center):
    aspect_ratio = min(bbox[2] / bbox[3], bbox[3] / bbox[2])
    aspect_term = aspect_ratio ** 0.5
    horiz = abs(target_center[0] - image_center[0]) / image_center[0]
    vert = abs(target_center[1] - image_center[1]) / image_center[1]
    center_term = 1.0 / (1.0 + (horiz + vert) * 1.5)
    return 0.5 * aspect_term + 0.3 * center_term + 0.2
```

```python
class AdaptivePerformanceManager:
    def __init__(self, target_hit_rate=0.4):
        self.target_hit_rate = target_hit_rate
        self.current_mode = "balanced"

    def update_mode(self, current_fps, target_count, time_pressure=False):
        if current_fps < 15 or time_pressure:
            self.current_mode = "fast"
        elif current_fps > 25 and target_count <= 3:
            self.current_mode = "precise"
        else:
            self.current_mode = "balanced"
        return self.current_mode

    def get_detection_stride(self):
        return {"fast": 3, "balanced": 2, "precise": 1}[self.current_mode]
```

## 运行流程

### 初始化阶段

1. 载入配置：摄像头参数、PID 系数、Omega 权重、串口地址。
2. 打开摄像头，设置 640×480@30fps，执行自检。
3. 加载 YOLOv8n 模型并切换到 FP16 推理模式。
4. 串口握手：使用 `bot.sdk.enter_sdk_mode()`，校验云台响应。
5. 运行焦距校准（若有标定数据则加载缓存）。

### 主循环步骤（每帧）

1. **采集**：抓取最新帧并记录时间戳。
2. **性能评估**：更新 FPS，决定 YOLO 是否执行（stride = 1/2/3）。
3. **检测 & 筛选**：执行 YOLO → 去噪 → 输出候选集。
4. **评分**：对候选计算距离、角度、Omega 分值，选择最佳目标。
5. **姿态计算**：完成测距与角度解算。
6. **控制输出**：通过 PID 平滑角度增量，调用 `bot.conn.write_serial()` 下发。
7. **监控**：记录帧率、命中统计、串口状态，必要时调整性能模式。

## 异常处理策略

- **目标短时丢失 (<10 帧)**：沿历史速度预测下一位置或保持上一控制量。
- **目标长时丢失**：触发扫描模式（云台缓慢扫扇形），或将控制权交回手动技能。
- **串口写失败**：最多重试 3 次；失败后调用 `enter_safe_mode()`，停止发射并记录日志。
- **模型推理异常**：退回 fast 模式并生成 WARN 日志，等下一帧重试。

## 参数与配置建议

```python
CAMERA_CONFIG = {
    "resolution": (640, 480),
    "fps": 30,
    "exposure": "auto",
    "white_balance": "auto"
}

DISTANCE_ESTIMATION = {
    "real_armor_width": 0.13,
    "real_armor_height": 0.05,
    "min_effective_distance": 1.0,
    "max_effective_distance": 8.0
}

OMEGA_WEIGHTS = {
    "fast": (0.7, 0.3),
    "balanced": (0.6, 0.4),
    "precise": (0.5, 0.5)
}

PID_PARAMS = {
    "yaw": {"kp": 0.08, "ki": 0.001, "kd": 0.02, "max_output": 30},
    "pitch": {"kp": 0.08, "ki": 0.001, "kd": 0.02, "max_output": 30}
}
```

将上述配置写入 `config/aimassistant.yaml`（可新建），由 pipeline 在启动时加载。

## 与现有框架的集成点

- 在 `main.py` 中引入 Aim Assistant pipeline，作为技能或后台控制任务注册到 `SkillManager`。
- `recognizer.py` 可复用摄像头与 YOLO 初始化逻辑；也可由 Aim Assistant 自带管线并与 `recognizer` 共享模型权重。
- 通过 `bot.conn.start_serial_worker()` 获取串口命令，同时监听键鼠触发（例如按键启/停自瞄）。
- 控制输出应遵循 `bot` 模块既有接口（`gimbal.py`、`blaster.py`），避免直接拼串口字符串。
- 日志统一使用 `import logger as LOG`，告警/异常需包含上下文（帧号、目标 ID、当前模式）。

## 调试与验证流程

1. 使用 `python -m src.repl` 观察串口指令与云台反馈。
2. 开启可视化调试：绘制目标框、估算距离、当前模式，窗口可复用 OpenCV 显示。
3. 编写 `tests/test_aimassistant.py`：
   - 单元测试 `MonocularDistanceEstimator`、Omega 评分函数。
   - 使用截图或录制片段做离线推理验证。
4. 性能测试：记录每帧处理时间、CPU/GPU 占用，分析自适应模式切换的稳定性。

## 面向 AI 协作者的待办清单

- [ ] 构建 `src/model/aimassistant/` 初始结构与数据管线。
- [ ] 编写配置加载器与运行参数自检逻辑。
- [ ] 实现并单测距离估计、角度解算、Omega 评分、Adaptive Manager。
- [ ] 实装云台 PID 控制与弹道补偿（可参考现有 `bot` 接口）。
- [ ] 打通技能触发链路：按键启停、目标丢失转手动、命中统计反馈。
- [ ] 设计可视化面板，展示实时目标、模式、补偿角度与串口状态。

## 未来拓展方向

- 引入相机标定矩阵替代简化焦距估计，提升角度精度。
- 加入目标运动预测（卡尔曼滤波或短期轨迹拟合）。
- 对 YOLO 模型进行剪枝/量化或 Distillation，以提升树莓派运行帧率。
- 研究双目或深度相机方案，实现更可靠的距离估计。
- 扩展到多机器人协同瞄准，共享目标信息与弹道规划。

---
本指南帮助参与自瞄模块开发的 AI 迅速进入状态。请在实现新特性后同步更新此文档，使团队与自动化工具始终对齐最新设计。
