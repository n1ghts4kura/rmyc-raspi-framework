---
title: 自瞄系统模块总览（Aim Assistant Intro）
version: 2025-11-23
status: draft
category: intro
last_updated: 2025-11-23
tags:
	- aimassistant
	- vision
	- skill
	- gimbal
---

# 自瞄系统模块总览（Aim Assistant Intro）

> 本文档介绍 `src/aimassistant/` 模块在整个框架中的定位、内部结构和输入/输出数据流，
> 只关注**当前设计与职责边界**，不复盘历史与踩坑（详见 `journey/aimassistant_journey.md`）。

---

## 1. 模块定位与职责

自瞄系统（`aimassistant`）位于「视觉识别 → 行为控制」链路的中间层，其核心职责是：

- 从视觉识别模块 `recognizer` 获取最新目标检测结果；
- 在多个候选目标中选择一个“当前最应该瞄准”的目标；
- 根据目标在画面中的位置，计算云台需要转动的偏航角（yaw）和俯仰角（pitch）；
- 将解算出的角度指令交给云台控制（`bot/gimbal`）或上层技能（`skill/autoaim`）使用。

换句话说：

- **aimassistant 不做图像预处理和模型推理**（这些在 `recognizer` 内完成）；
- **aimassistant 不直接控制底盘/发射器协议细节**（这些在 `bot/` 层完成）；
- aimassistant 只负责「从检测框 → 目标选择 → 角度偏差 → 控制指令」的中间决策逻辑。

---

## 2. 内部子模块结构

当前 `src/aimassistant/` 目录下主要包含三个核心文件：

- `angle.py`：角度解算模块，负责根据检测框位置和相机 FOV 计算 yaw/pitch 偏差；
- `selector.py`：目标选择模块，在多目标场景下根据面积、中心度、置信度等因子选出“最佳目标”；
- `pipeline.py`：自瞄工作管线，组织一次完整自瞄步骤的执行顺序（检测 → 选择 → 解算 → 控制）。

下面分别说明三个子模块的职责与输入/输出。

### 2.1 `angle.py`：角度解算模块

文件：`src/aimassistant/angle.py`

主要公开函数：

- `calculate_angles(box: Boxes) -> tuple[float, float]`
	- 输入：
		- `box`: YOLO 检测结果中的单个 `Boxes` 对象，使用 `xywhn` 归一化格式（中心点 + 宽高，范围 [0,1]）。
	- 输出：
		- `(yaw, pitch)`: 云台需要转动的角度偏差（单位：度），
			- `yaw`：水平偏航角，向右为正，近似等于「水平 FOV × 水平归一化偏移量」；
			- `pitch`：垂直俯仰角，向上为正，考虑了图像长宽比推导出的垂直 FOV。

核心思路（简化说明）：

1. 从 `box.xywhn[0]` 中取出归一化中心坐标 `(center_x_n, center_y_n)`；
2. 计算相对图像中心 `(0.5, 0.5)` 的归一化偏移 `dx_norm`, `dy_norm`；
3. 使用针孔相机模型，根据配置 `config.CAMERA_FOV_HORIZONTAL` 推导垂直 FOV；
4. 将归一化偏移映射为角度：
	 - `yaw = dx_norm * CAMERA_FOV_HORIZONTAL`
	 - `pitch = -dy_norm * FOV_VERTICAL`

> 详细推导与调参过程，可参考 `journey/aimassistant_journey.md` 与性能相关的 journey 文档。

### 2.2 `selector.py`：目标选择模块

文件：`src/aimassistant/selector.py`

主要公开函数：

- `selector_v1(boxes: Boxes) -> Boxes`
	- 输入：
		- `boxes`: 多个候选目标的 `Boxes` 集合（YOLO 检测输出）。
	- 输出：
		- `Boxes`: 被选为“当前瞄准目标”的单个框对象。

选择策略 v1（高层描述）：

- 为每个目标计算三个因子：
	- **面积因子**（`box_square_factor_v1`）：
		- 检测框越大，认为目标越近或越重要；
	- **中心度因子**（`box_center_factor_v1`）：
		- 目标中心越接近画面中心，得分越高；
	- **置信度因子**（`confidence_factor_v1`）：
		- 检测置信度越高，得分越高；
- 使用装饰器 `weight_setting(weight: float)` 为各因子分配权重，并确保权重和不超过 1.0；
- 综合得分：

	$$
	score = (area\_factor + center\_factor + confidence\_factor) \times v1\_weight
	$$

- 选择综合得分最高的检测框作为当前瞄准目标。

> 这一套策略保证了默认情况下自瞄更倾向于「画面中央附近、面积较大且置信度高」的目标。

### 2.3 `pipeline.py`：自瞄工作管线

文件：`src/aimassistant/pipeline.py`

主要公开函数：

- `aim_step_v1(recognizer: Recognizer) -> bool`
	- 输入：
		- `recognizer`: 视觉识别器实例（`src/recognizer.py` 中的 `Recognizer`），要求已在独立线程/流程中启动并持续更新检测结果；
	- 输出：
		- `bool`: 本次自瞄是否成功发送了控制指令：
			- `True`：检测到有效目标，并完成目标选择、角度解算与控制命令发送；
			- `False`：未检测到目标或识别器尚未就绪。

函数内部主要步骤：

1. 调用 `recognizer.get_latest_boxes()` 获取最近一帧的检测结果；
2. 若无检测结果（`None` 或空列表），直接返回 `False`；
3. 调用 `selector_v1` 从多目标中选出最佳目标 `best_box`；
4. 调用 `calculate_angles(best_box)` 计算 `(yaw_offset, pitch_offset)`；
5. 调用 `bot.gimbal.rotate_gimbal(...)` 发送云台相对角度控制指令：
	 - 使用 `config.GIMBAL_SPEED` 作为 yaw/pitch 速度；
	 - 设计上为**非阻塞调用**，不等待云台运动完成；
6. 打印调试日志并返回 `True`。

> `pipeline.py` 是上层技能（如 `skill/autoaim`）的主要入口，一般在自瞄技能每一帧/每一次 Tick 时调用 `aim_step_v1`。

---

## 3. 数据流与接口边界

### 3.1 上游：视觉识别模块 `recognizer`

- 上游模块：`src/recognizer.py` 中的 `Recognizer` 类；
- 关键接口：
	- `recognizer.get_latest_boxes()`：返回最近一帧推理结果的 `Boxes` 集合；
- 约定：
	- recognizer 负责模型加载、推理线程管理和结果缓存；
	- aimassistant 只关心「最新一次有效检测」，不处理摄像头细节、模型文件路径等问题。

### 3.2 aimassistant 内部数据流

概念流向：

1. `Recognizer` 生成 `Boxes`（多个候选目标）；
2. `selector_v1` 从 `Boxes` 中挑选一个最佳目标 `best_box`；
3. `calculate_angles(best_box)` 生成 `(yaw_offset, pitch_offset)`；
4. `rotate_gimbal(...)` 根据偏差角度控制云台；
5. 上层技能根据返回值（True/False）决定是否进入搜索模式、是否尝试开火等后续动作。

### 3.3 下游：技能系统与硬件控制

- 技能系统：`src/skill/autoaim.py` 等文件，会在自身主循环中周期性调用 `aim_step_v1`；
- 硬件控制：
	- `bot/gimbal.rotate_gimbal(...)`：接受角度偏差与速度，转换为实际云台控制指令；
	- 未来也可以扩展：基于 aimassistant 的输出决定是否触发 `bot/blaster` 开火。

> aimassistant 与硬件协议的解耦原则：
> - angle/selector/pipeline 不直接关心串口协议细节；
> - 若协议或控制方式调整，应尽量在 `bot/` 层完成适配，而不是在 aimassistant 中堆积协议逻辑。

---

## 4. 典型调用流程（伪代码）

下面是自瞄链路在运行时的一个简化伪代码示意，帮助理解各模块之间的调用关系：

```python
# 伪代码：自瞄主循环中的典型调用方式

recognizer = Recognizer(...)
recognizer.start_inference_thread()

while autoaim_skill_is_active():
		boxes = recognizer.get_latest_boxes()
		if not boxes:
				continue  # 没有目标，可能进入搜索模式

		best_box = selector_v1(boxes)
		if best_box is None:
				continue

		yaw_offset, pitch_offset = calculate_angles(best_box)

		rotate_gimbal(
				pitch=pitch_offset,
				yaw=yaw_offset,
				vpitch=config.GIMBAL_SPEED,
				vyaw=config.GIMBAL_SPEED,
		)

		# 后续可以由技能层根据策略决定是否触发开火
```

> 实际工程中，上述逻辑会包装在 `aim_step_v1` 与技能系统内部，
> 并与多线程推理、性能调度等机制结合；本示例只用于说明数据与调用顺序。

---

## 5. 运行模式与性能假设

- 调用频率：
	- aimassistant 通常由自瞄技能周期性调用，频率与视觉推理 FPS 接近（目标为 4+ FPS，详见 `journey/performance_journey.md`）。
- 性能假设：
	- 角度计算与目标选择计算量较小，性能瓶颈主要在：
		- 视觉推理本身（模型大小、推理后端）；
		- 树莓派的电源与 CPU governor 设置；
		- 串口通信与云台反馈延迟。
- 线程模型：
	- 典型设计为「推理线程 + 控制主循环」：
		- 推理线程不断更新 `latest_boxes`；
		- 控制主循环在每次 Tick 中调用 `aim_step_v1` 读取最新结果并下发控制。

> 若出现 FPS 掉到 1FPS 或明显卡顿的问题，应优先参考 `journey/performance_journey.md`，
> 检查电源、CPU governor、推理后端与线程模型，而不是在 aimassistant 内部试图“硬抠”微优化。

---

## 6. 相关配置项与依赖

### 6.1 关键配置项（`config.py`）

- `CAMERA_FOV_HORIZONTAL: float`
	- 用于角度解算，决定从归一化偏移到实际 yaw/pitch 的映射比例；
	- 需要根据实际相机参数进行校准。
- `CAMERA_WIDTH: int`, `CAMERA_HEIGHT: int`
	- 用于计算垂直 FOV 和图像长宽比，影响 pitch 解算结果；
- `GIMBAL_SPEED: int`
	- 作为 `rotate_gimbal` 的速度参数（`vpitch` / `vyaw`），影响云台转动响应速度与稳定性；
- 未来可能新增的自瞄相关配置：
	- 目标丢失帧数阈值、搜索模式参数、不同目标类型的优先级等。

### 6.2 代码依赖关系

- 直接依赖：
	- `recognizer.Recognizer`
	- `bot.gimbal.rotate_gimbal`
	- `config` 中的相机与云台相关配置
- 间接依赖：
	- YOLO/Ultralytics 的 `Boxes` 数据结构；
	- 底层串口与硬件协议（通过 `bot/` 层封装）。

---

## 7. 推荐阅读与后续扩展

若需要更深入理解自瞄系统的演进与设计取舍，建议阅读：

- `journey/aimassistant_journey.md`
	- 记录了自瞄从最初版本到当前版本的设计过程、坑点和决策；
- `journey/performance_journey.md`
	- 记录了从约 1FPS 到 4+ FPS 的性能调优过程，特别是与视觉、自瞄相关的调优经验；
- `general_intro.md`
	- 了解整个项目的架构与模块分层，自瞄只是其中一环；
- 未来计划中的文档：
	- `vision_intro.md`：视觉识别与模型链路的整体说明；
	- `skill_intro.md`：技能系统结构与生命周期说明。

> 本文档将随着自瞄逻辑与依赖的演进持续更新，
> 当你对 aimassistant 的职责边界或接口产生疑问时，应优先以本 intro 为事实来源，
> 再结合 journey 与源码进行深入分析。
