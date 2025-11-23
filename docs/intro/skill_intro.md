---
title: 技能系统模块总览（Skill Intro）
version: 2025-11-23
status: draft
category: intro
last_updated: 2025-11-23
tags:
  - skill
  - gameplay
  - input
  - autoaim
---

# 技能系统模块总览（Skill Intro）

> 本文档基于 `src/skill/*` 与 `src/bot/game_msg.py`，说明技能系统的职责、生命周期、按键映射模型
> 以及与自瞄/硬件控制的协作关系，作为“一切与键盘输入触发行为相关”的事实入口。

---

## 1. 模块定位与职责

技能系统由 `src/skill/` 目录下的模块组成，核心目标是：

- 将“键盘/鼠标等输入事件”抽象为“技能（Skill）”；
- 为每个技能提供独立的生命周期与线程上下文；
- 统一管理技能的添加、启用、取消与状态查询；
- 把复杂的行为（如自瞄循环、联动控制）封装在技能内部，而不是散落在主循环。

与其他模块的边界：

- **技能系统不直接读串口 / SDK 数据**，而是依赖 `bot/game_msg.py` 把赛事输入解析为“按键列表”；
- **技能系统不直接操纵底盘/云台/发射器协议细节**，而是调用 `bot/*` 层提供的语义化 API（如 `rotate_gimbal`）；
- 技能内部可以调用 `aimassistant`、`recognizer` 等高层模块，但不改动它们的底层实现。

---

## 2. 核心组成结构

当前技能系统由三部分组成：

- `BaseSkill`（`src/skill/base_skill.py`）：单个技能的抽象与线程封装；
- `SkillManager`（`src/skill/manager.py`）：技能注册、按键调度与启用/取消逻辑；
- 具体技能实现（例如 `src/skill/autoaim.py` 与 `src/skill/example_skill.py`）。

下面分别介绍它们的职责与典型用法。

### 2.1 `BaseSkill`：单个技能抽象

文件：`src/skill/base_skill.py`

主要职责：

- 描述“一个技能”的基本属性：绑定按键、名称、当前线程、启用状态；
- 提供统一的 `invoke()` / `cancel()` 接口，封装线程创建与结束的细节；
- 为技能实现代码提供一个 `BaseSkill` 自身引用，用于在技能内部检查 `enabled` 状态。

核心设计：

- 构造函数：
  - 参数：`binding_key: str`, `invoke_func: Callable`, `name: str | None = None`；
  - 行为：
    - 将绑定按键统一转换为小写（方便与输入解析结果对齐）；
    - 保存回调函数 `invoke_func(self, ...)`；
    - 若未指定名称，默认使用 `[binding_key]` 作为技能名称。
- `invoke(*args, **kwargs) -> None`：
  - 创建守护线程 `threading.Thread(target=self.invoke_func, args=(self, ) + args, ...)`；
  - 启动线程，并将 `self.enabled` 置为 `True`；
  - 典型用法：在 Manager 中根据按键触发，或在测试脚本中手动调用。
- `cancel() -> None`：
  - 若线程仍然存活则 `join(timeout=5)` 等待结束；
  - 最终将 `self.enabled` 置为 `False`；
  - 线程退出的具体方式由技能实现决定（通常在循环中检查 `skill.enabled`）。

> 约定：技能本体逻辑应当对 `skill.enabled` 做适当检查，以便在外部调用 `cancel()` 时能尽快结束线程。

### 2.2 `SkillManager`：技能注册与调度

文件：`src/skill/manager.py`

主要职责：

- 维护一个 `skills: list[BaseSkill]` 列表；
- 负责技能的注册（防止按键冲突）、按键触发调用与取消；
- 为上层调用（主循环/输入处理逻辑）提供简洁的接口。

关键方法：

- `add_skill(skill: BaseSkill) -> None`：
  - 检查是否有已有技能使用了同一个 `binding_key`，如有则记录错误日志并抛出 `ValueError`；
  - 若无冲突，则将技能加入管理列表并输出 INFO 日志。
- `get_skill_enabled_state(binding_key: str) -> bool`：
  - 遍历技能列表，找到对应按键技能并返回其 `enabled` 状态；
  - 若未找到对应技能，则返回 `False`（不抛异常）。
- `invoke_skill_by_key(binding_key: str, *args, **kwargs) -> bool`：
  - 根据按键找到技能并调用其 `invoke()`；
  - 输出 INFO 日志，并返回 `True` 表示触发成功；
  - 若无匹配技能，输出 WARN 日志并返回 `False`。
- `cancel_skill_by_key(binding_key: str) -> bool`：
  - 根据按键找到技能并调用其 `cancel()`；
  - 输出 INFO 日志，并返回 `True` 表示取消成功；
  - 若无匹配技能，输出 WARN 日志并返回 `False`。

### 2.3 具体技能示例：自瞄技能 `autoaim`

文件：`src/skill/autoaim.py`

结构：

- 技能执行函数：`auto_aim_action(skill: BaseSkill)`；
- 技能实例：
  ```python
  auto_aim_skill = BaseSkill(
      binding_key="z",
      invoke_func=auto_aim_action,
      name="自动瞄准"
  )
  ```

执行逻辑概览：

- 通过 `Recognizer.get_instance()` 获取视觉识别器；
- 读取 `recognizer.get_status()` 估算实际推理 FPS，用于计算搜索步进角度；
- 在循环中不断调用 `aimassistant.pipeline.aim_step_v1(recognizer)`：
  - 若成功锁定目标，则重置“无目标帧数计数器”；
  - 若连续多帧无目标（`config.AIM_LOST_TARGET_TIMEOUT_FRAMES`），根据 `config.AIM_SEARCH_FOV_COVERAGE` 与 `config.GIMBAL_SPEED` 计算搜索旋转角度，调用 `rotate_gimbal(...)` 进行云台搜索；
- 每一轮循环后 `time.sleep(1.0 / config.AIM_CONTROL_FREQUENCY)` 控制整体调用频率；
- 循环条件依赖 `skill.enabled`，当外部取消技能或发生异常时，线程自然退出。

> 这个例子展示了技能如何组合视觉识别（`Recognizer`）、自瞄决策（`aimassistant`）与硬件控制（`bot.gimbal`），形成一个完整的高层行为。

---

## 3. 输入来源与按键映射

### 3.1 赛事输入解析（`bot/game_msg.py`）

- 赛事数据通过底层串口以字符串形式推送到上位机，例如：
  - `game msg push [0, 6, 1, 0, 0, 255, 1, 199];`
- `game_msg_process(data: str) -> GameMsgDictType` 将其解析为字典，包括：
  - 鼠标状态（右键/左键/中键）、鼠标位移；
  - 按键数量 `key_num` 与按键编码列表 `keys`；
- 目前使用简单映射 `chr(int(x) - 80)` 将数值编码转换为小写字母（例如 199 → 'w'），
  这一映射规则在代码注释中通过推导说明，并标记为今后可完善的 TODO。

### 3.2 从按键到技能

- 在主程序或输入分发逻辑中，可按如下模式使用技能系统：

```python
from skill.manager import SkillManager
from skill.autoaim import auto_aim_skill

manager = SkillManager()
manager.add_skill(auto_aim_skill)

# 在某个输入循环中：
for key in parsed_keys:  # parsed_keys 来自 game_msg_process 的解码结果
    # 再次按相同键可以调用 cancel_skill_by_key 实现“开关式”技能
    manager.invoke_skill_by_key(key)
```

- 推荐实践：
  - 将“按一次键 = 开启技能 / 再按一次 = 取消技能”的开关行为封装在更高一层逻辑中，
    通过 `get_skill_enabled_state()` 判断当前状态，再决定是调用 `invoke` 还是 `cancel`；
  - 把“按键 → 技能”的绑定关系集中在一个地方（例如初始化阶段），避免散落在多处脚本中。

---

## 4. 生命周期与协作模式

### 4.1 技能生命周期

- 创建阶段：
  - 定义技能执行函数 `def some_action(skill: BaseSkill, ...)`；
  - 使用 `BaseSkill(binding_key="x", invoke_func=some_action, name="...")` 创建实例；
  - 通过 `SkillManager.add_skill(...)` 注册到技能系统；
- 运行阶段：
  - 当检测到对应按键时，调用 `invoke_skill_by_key(binding_key)` 启动技能线程；
  - 技能执行函数内部通常包含一个 `while skill.enabled:` 循环；
- 结束阶段：
  - 外部调用 `cancel_skill_by_key(binding_key)`，或设置某个条件使技能线程自然退出；
  - `BaseSkill.cancel()` 负责等待线程结束并清理状态标志。

### 4.2 与其他模块协作

- 与视觉/自瞄：
  - 技能可以获取 `Recognizer` 实例，并调用 `aimassistant` 的管线函数（如 `aim_step_v1`）；
  - 视觉与自瞄逻辑独立维护，技能只负责“何时调用”“如何响应无目标情况”等策略；
- 与硬件控制：
  - 技能通过 `bot/` 层 API 控制云台、底盘或发射器，例如 `rotate_gimbal`、`set_gimbal_recenter` 等；
  - 协议细节/安全范围封装在 `bot/` 模块中，技能不直接拼写串口指令；
- 与 REPL：
  - REPL 更适合作为调试和验证技能行为的工具（例如单独测试云台搜索、按键绑定等），
    这些场景可在 `docs/guide/repl.md` 中补充示例。

---

## 5. 推荐阅读与后续扩展

- `docs/intro/aimassistant_intro.md`
  - 理解技能如何调用自瞄管线，将视觉结果转化为云台控制行为；
- `docs/intro/vision_intro.md`
  - 了解视觉模块如何产出 `Boxes`，以及性能假设与状态观测方式；
- `docs/reference/sdk_protocol_api_document.md`
  - 熟悉底层 SDK 协议与常用命令，为编写新技能（尤其是直接控制底盘/发射器的技能）提供参考；
- 未来规划中的文档：
  - `docs/journey/skill_system_journey.md`：记录技能系统从简单按键映射到复杂战术行为的演进历程；
  - 更多技能示例文档（例如“巡逻技能”“一键回城”等），展示如何在现有架构上安全扩展新行为。

> 当你需要新增或调整技能时，建议先阅读本 intro，再对照 `aimassistant_intro` 与视觉/硬件相关文档，
> 以确保技能职责边界清晰、生命周期可控，并与既有输入/控制通路保持一致。
