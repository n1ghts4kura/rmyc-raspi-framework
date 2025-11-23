---
title: 视觉识别模块总览（Vision Intro）
version: 2025-11-23
status: draft
category: intro
last_updated: 2025-11-23
tags:
  - vision
  - recognizer
  - yolo
  - performance
---

# 视觉识别模块总览（Vision Intro）

> 本文档基于 `src/recognizer.py` 与 `config.py`，说明当前视觉识别链路的职责、内部线程模型、关键接口与性能假设，
> 作为一切“视觉相关”问题（FPS、延迟、模型选择、与自瞄协作）的首选事实来源。

---

## 1. 模块定位与职责

视觉识别模块由 `src/recognizer.py` 中的 `Recognizer` 类实现，是整个系统的“目标检测入口”：

- 从摄像头高频采集图像帧；
- 使用 YOLO 模型（当前为 ONNX Runtime 后端）进行目标检测；
- 按照性能优化策略（预热 + 智能跳帧）持续产出最新一帧的检测结果；
- 为上层自瞄系统（`aimassistant`）、技能系统（`skill/*`）和调试工具（REPL）提供统一的检测结果接口。

换句话说：

- **Recognizer 不负责自瞄逻辑**，只输出“这一帧看到了哪些目标”；
- **Recognizer 不直接控制硬件**（底盘/云台/发射器），而是交由 `bot/` 和技能系统处理；
- Recognizer 的核心目标是：在树莓派这一硬件条件下，尽可能稳定地提供 4 FPS 左右的检测结果，并暴露可观测的运行状态。

---

## 2. 内部结构与线程模型

### 2.1 单例模式与基本配置

- `Recognizer` 采用单例模式（`get_instance()`），避免重复初始化摄像头与模型；
- 初始化参数（带默认值）：
  - `cam_width=480`, `cam_height=320`: 摄像头采集分辨率；
  - `imshow_width=240`, `imshow_height=160`: 调试窗口显示分辨率；
  - `cam_fps=60.0`: 摄像头目标帧率（硬件和驱动实际能到多少视情况而定）。
- 关键成员：
  - 摄像头句柄：`self.cap: cv2.VideoCapture`；
  - 模型实例：`self.model: YOLO`（使用 `config.YOLO_MODEL_PATH`）；
  - 结果缓存：`self._latest_boxes: Boxes`，始终保存“最近一次检测结果”；
  - 内部队列：`self._frame_queue: queue.Queue`，生产者/消费者在线程间传递原始帧；
  - 状态锁：`self._state_lock`，保护 `_initialized` 与 `_latest_boxes`。

### 2.2 双线程结构

Recognizer 使用「采集线程 + 推理线程」的结构：

- 采集线程 `_capture_thread`：
  - 目标：尽可能稳定、高频地从摄像头读取原始帧；
  - 行为：
    - 不断调用 `self.cap.read()` 获取帧；
    - 若队列已满，丢弃旧帧（`get_nowait()`）再放入新帧，减少积压；
    - 通过 `self._frame_queue` 将帧交给推理线程。
- 推理线程 `_infer_thread`：
  - 目标：在当前硬件上以最大速度消化最新帧，并保持平均 FPS 信息可观测；
  - 行为：
    1. 等待首帧作为预热输入；
    2. 使用真实帧对模型进行多次预热推理（解决首次推理长延迟）；
    3. 清空预热期间积累的旧帧，设置 `_initialized=True`；
    4. 启动“智能跳帧 + 最大速度”循环：
       - 非阻塞、多次 `get_nowait()` 清空队列，只保留最新帧；
       - 对最新帧调用 `_process_frame()`，更新 `_latest_boxes` 与统计信息；
       - 不主动 `sleep`，在当前性能目标下由推理本身自然控制节奏。

> 线程绑定：代码中尝试使用 `os.sched_setaffinity` 将采集线程绑定到 CPU 核 0，将推理线程绑定到 2/3，以期在树莓派上提高整体稳定性；不支持时会静默忽略。

---

## 3. 关键接口与数据流

### 3.1 对外接口

Recognizer 对上层模块暴露的主要方法包括：

- `Recognizer.get_instance(**kwargs) -> Recognizer`
  - 获取全局唯一实例；仅第一次调用时会使用参数，其后忽略；
- `start() -> bool`
  - 初始化摄像头与模型，启动采集/推理线程；若已在运行则返回 False；
- `stop() -> None`
  - 停止线程、重置 `_initialized` 标志；
- `wait_until_initialized(timeout: float = 120) -> bool`
  - 阻塞等待直到完成预热并设置 `_initialized=True` 或超时；
- `is_running() -> bool`
  - 检查采集/推理线程是否都处于活跃状态；
- `get_latest_boxes() -> Boxes`
  - 获取“最近一次推理结果”的 `Boxes` 对象；线程安全；
- `get_status() -> dict`
  - 返回包含初始化状态、线程存活情况、队列长度、最新目标数量、已推理帧数、丢帧数、实际推理 FPS 等信息的字典。

### 3.2 数据流概览

1. 摄像头 → 采集线程：
   - `cv2.VideoCapture` 按设定分辨率与帧率读取帧；
2. 采集线程 → 队列：
   - 若队列满，丢弃一帧旧数据，再放入当前最新帧；
3. 队列 → 推理线程：
   - 推理线程连续 `get_nowait()` 清空队列，只保留最后一帧作为当前推理输入；
4. 推理线程 → YOLO 模型：
   - 在 `_process_frame()` 中调用 `self.model.predict(...)` 获取检测结果；
   - 结果为 `results[0].boxes`（`Boxes` 类型）；
5. 推理线程 → 结果缓存：
   - 持有 `_state_lock`，将 `_latest_boxes` 更新为最新 `Boxes`；
6. 上层模块（自瞄/技能/调试）通过 `get_latest_boxes()` 读取结果：
   - 例如 `aimassistant.pipeline.aim_step_v1(recognizer)` 使用此接口获取当前帧目标列表。

---

## 4. 模型与图像预处理

### 4.1 模型配置

- 模型路径：`config.YOLO_MODEL_PATH`（当前为 `./model/yolov8n.onnx`）；
- 模型类型：使用 `ultralytics.YOLO`，通过 ONNX Runtime 后端加载；
- 预热策略：
  - 在 `_init_model()` 中，先用一个全零的虚拟图像进行多次推理预热；
  - 在 `_infer_loop()` 中，再使用真实帧预热模型 3 次，并清空期间旧帧；
- 检测阈值：
  - 置信度阈值：`self.conf = 0.3`；
  - IOU 阈值：`self.iou = 0.7`；
  - 推理设备：`self.device = "cpu"`（当前默认设为 CPU）。

> 与模型格式选择、ONNX 导出与性能对比相关的历史经验，记录在 `docs/journey/performance_journey.md` 中。

### 4.2 图像预处理（Gamma 校正）

- 开关：`config.ENABLE_IMAGE_PREPROCESSING`（默认 True）；
- 算法：使用 `src.utils.adjust_gamma` 对输入帧做 Gamma 校正；
- 当前参数：`config.IMAGE_PREPROCESSING_GAMMA = 0.8`；
- 设计约束：
  - 训练数据采集与部署时的预处理必须保持一致；
  - 修改 Gamma 后需要重新采集/训练模型；
  - 预处理已经通过 LUT 做缓存，性能开销较小。

> 训练数据采集脚本位于 `training/data_collector.py`，相关经验可在未来的 `vision_recognition_journey.md` 中进一步记录。

---

## 5. 性能与状态观测

### 5.1 性能假设与目标

- 目标：在树莓派上通过 ONNX Runtime 达到约 4 FPS 的稳定推理速度；
- 性能瓶颈：
  - 模型推理本身（模型大小、输入尺寸、后端实现）；
  - 树莓派 CPU 性能与电源/CPU governor 设置；
  - 摄像头驱动与 USB 带宽。

> 详细的 FPS 提升历程与优化步骤可参见 `docs/journey/performance_journey.md`。

### 5.2 `get_status()` 输出字段

- `initialized`: 是否完成预热并标记为就绪；
- `running`: 采集/推理线程是否均在运行；
- `capture_thread_alive`, `infer_thread_alive`: 各线程是否存活；
- `stop_event_set`: 停止事件是否已触发；
- `queue_size`: 当前队列中待推理的帧数；
- `latest_boxes_count`: 最近一次检测出的目标数量；
- `camera_opened`: 摄像头是否成功打开；
- `model_loaded`: 模型是否成功加载；
- `predict_frame_count`: 累计推理帧数；
- `dropped_frame_count`: 为保持实时性而丢弃的帧数；
- `actual_inference_fps`: 从推理开始到目前为止的平均推理 FPS。

这些字段可用于：

- 在 REPL 或调试界面中实时观察视觉模块状态；
- 在性能调优或异常排查时快速判断瓶颈位置（摄像头/模型/线程）。

---

## 6. 与其他模块的协作关系

### 6.1 与自瞄模块（`aimassistant`）

- 自瞄管线通过 `aimassistant.pipeline.aim_step_v1(recognizer)` 使用视觉结果：
  - 调用 `recognizer.get_latest_boxes()` 获取最新 `Boxes`；
  - 交由 `selector_v1` 选择目标，再由 `calculate_angles` 计算 yaw/pitch 偏差；
- 视觉模块不关心目标怎么被使用，只保证“尽可能新鲜”的检测结果；
- 视觉与自瞄之间的耦合点：
  - 分辨率与相机内参（FOV）需要一致，具体由 `config` 与 `aimassistant` 协同使用。

### 6.2 与技能系统与主程序

- 技能系统（如 `skill/autoaim.py`）通常会在自己的主循环中：
  - 通过 `Recognizer.get_instance()` 获取识别器；
  - 确保识别器已经 `start()` 并 `wait_until_initialized()`；
  - 在每一帧调用自瞄或其他使用视觉结果的逻辑；
- 主程序（`src/main.py`）负责在系统启动时初始化识别器，并根据当前技能配置决定是否启用视觉链路。

### 6.3 与 REPL 与调试工具

- 未来可以在 REPL 中提供子命令：
  - 查询 `get_status()` 输出；
  - 临时调整置信度阈值、是否启用图像预处理等参数（需与配置管理协调）；
- 这些场景建议在 `docs/guide/repl.md` 与未来的 `vision_recognition_journey.md` 中进行补充说明。

---

## 7. 推荐阅读与后续扩展

- `docs/journey/performance_journey.md`
  - 了解从 1 FPS 到 4+ FPS 的性能优化路径，包括 ONNX Runtime 选择、电源与 CPU governor 设置以及线程模型调整；
- `docs/intro/aimassistant_intro.md`
  - 理解视觉检测结果如何被自瞄模块消费，完成“检测 → 目标选择 → 角度解算 → 云台控制”的闭环；
- 未来规划中的文档：
  - `docs/journey/vision_recognition_journey.md`：专门记录视觉链路的演进、模型选择、预处理策略与调参经验；
  - `docs/guide/troubleshooting_vision.md`：收集常见视觉问题（黑屏、FPS 过低、检测不稳定）的排查步骤。

> 当你需要修改视觉模块（更换模型、调整分辨率、优化性能）时，建议优先阅读本 intro 与性能、自瞄相关 journey，
> 以保证改动方向与现有架构、性能目标保持一致。
