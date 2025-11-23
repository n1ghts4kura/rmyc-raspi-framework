---
title: 硬件抽象层总览（Bot Intro）
version: 2025-11-23
status: draft
category: intro
last_updated: 2025-11-23
tags:
  - bot
  - hardware
  - sdk
  - gimbal
  - chassis
  - blaster
---

# 硬件抽象层总览（Bot Intro）

> 本文档基于 `src/bot/*` 与 `docs/reference/sdk_protocol_api_document.md`，
> 说明本项目对 RoboMaster 明文 SDK 的二次封装方式，包括串口连接、SDK 模式切换、底盘/云台/发射器控制等，
> 作为一切“硬件控制相关”问题的事实入口。

---

## 1. 模块定位与职责

`src/bot/` 目录承载了对 RoboMaster SDK 的“硬件抽象层”（Hardware Abstraction Layer, HAL）：

- 通过 `conn.py` 管理串口连接与后台接收线程；
- 通过 `sdk.py` 进入/退出 SDK 模式；
- 通过 `robot.py`、`chassis.py`、`gimbal.py`、`blaster.py`、`game_msg.py` 等模块，
  以**带类型检查与参数校验的 Python 函数**封装底盘/云台/发射器与赛事数据输入；
- 避免上层（技能、自瞄、调试工具）直接拼接字符串协议；
- 对照 `docs/reference/sdk_protocol_api_document.md`，保持与官方协议的参数范围与语义一致。

换句话说：

- **bot 层负责“把字符串协议变成人类友好的 API”**；
- 上层模块（`skill/*`, `aimassistant/*`, `repl` 等）应尽量只调用这些 API，而不要自己写 `"chassis ...;"` 字符串；
- 所有与串口生命周期、下位机响应验证相关的逻辑集中在 `conn.py`，避免在多处重复处理。

---

## 2. 串口连接与后台接收（`conn.py`）

文件：`src/bot/conn.py`

主要职责：

- 根据 `config.SERIAL_PORT` 打开串口（`open_serial()`），并设置 Linux 设备权限；
- 启动后台接收线程，将串口字节流按“行”和“分号 `;` 分隔的命令”切分为两类队列：
  - 文本行队列：`get_serial_line_nowait()`；
  - 指令队列：`get_serial_command_nowait()`；
- 提供统一的 `write_serial(data: str) -> bool` 接口，带互斥锁与异常处理；
- 在关闭时（`close_serial()`）安全停止后台线程并释放句柄。

关键点：

- 打开串口时会：
  - 设置端口参数（115200 波特率，8N1 等）；
  - 启动 `_rx_worker_loop` 线程，循环读取 `in_waiting` 字节、按 CR/LF 或空闲超时分帧；
  - 发送一次 `command;` 测试命令，并在有限时间内等待任意非空响应，以确认下位机在线；
- 收到的数据既会进入“行队列”（方便日志/调试），也会被 `_cmd_buffer` 拼接按 `;` 切分成指令队列，
  方便在高层按命令粒度消费；
- 所有串口读写都受 `serial_conn_lock` 保护，降低竞争风险。

> 建议：在主程序启动时，优先调用 `open_serial()` 并检查返回值，再进入 SDK 模式与后续控制流程。

---

## 3. SDK 模式控制（`sdk.py`）

文件：`src/bot/sdk.py`

- `enter_sdk_mode() -> None`
  - 发送 `command;` 进入 SDK 模式；
  - 建议在串口连通且确认下位机在线后尽快调用；
- `exit_sdk_mode() -> None`
  - 发送 `quit;` 退出 SDK 模式；
  - 建议在程序退出前调用，或在 REPL 中提供显式命令。

这些命令与 `docs/reference/sdk_protocol_api_document.md` 中“SDK 模式控制”章节完全一致。

---

## 4. 机器人与底盘控制（`robot.py` & `chassis.py`）

### 4.1 机器人运动模式（`robot.py`）

- `set_robot_mode(mode: Literal["chassis_lead", "gimbal_lead", "free"] = "free") -> bool`
  - 上层通过该函数切换机器人模式：
    - `chassis_lead`: 云台 YAW 跟随底盘，云台 YAW 控制失效；
    - `gimbal_lead`: 底盘 YAW 跟随云台，底盘 YAW 控制失效；
    - `free`: 云台与底盘 YAW 分离（推荐自瞄使用）。
  - 内部会验证 `mode` 是否在允许列表，否则返回 False 而不下发命令；
  - 实际串口命令：`robot mode <mode>;`。

### 4.2 底盘控制（`chassis.py`）

主要函数：

- `set_chassis_speed_3d(speed_x: float, speed_y: float, speed_z: float) -> None`
  - 对应协议：`chassis speed x <speed_x> y <speed_y> z <speed_z>;`；
  - 参数范围：
    - `speed_x` ∈ [-3.5, 3.5] m/s（>0 向前）；
    - `speed_y` ∈ [-3.5, 3.5] m/s（<0 向左）；
    - `speed_z` ∈ [-600, 600] °/s；
  - 超出范围会抛 `ValueError`，而不是静默裁剪。

- `set_chassis_wheel_speed(w1: int, w2: int, w3: int, w4: int) -> None`
  - 对应协议：`chassis wheel w1 <speed_w1> w2 <speed_w2> w3 <speed_w3> w4 <speed_w4>;`；
  - 四轮速度范围均为 [-1000, 1000] rpm，超出抛 `ValueError`。

- `chassis_move(distance_x: float, distance_y: float, degree_z: int | None, speed_xy: float | None, speed_z: float | None, delay: bool = False) -> None`
  - 对应协议：`chassis move x <distance_x> y <distance_y> [z <degree_z>] [vxy <speed_xy>] [vz <speed_z>];`；
  - 参数范围：
    - `distance_x`/`distance_y` ∈ [-5, 5] m；
    - `degree_z` ∈ [-1800, 1800] °；
    - `speed_xy` ∈ (0, 3.5] m/s；
    - `speed_z` ∈ (0, 600] °/s；
  - 若 `delay=True`，会根据平移距离与旋转角度估算完成时间并 `sleep`（多加 0.5s 保险），
    因此在性能敏感场景中应谨慎开启。

---

## 5. 云台控制（`gimbal.py`）

文件顶部注释已经明确标出：**本模块存在阻塞函数，且默认开启阻塞**，使用时务必考虑线程与实时性影响。

### 5.1 低层控制函数

- `_move_gimbal(pitch, yaw, vpitch, vyaw)`（相对角度，非阻塞）
  - 直接对应协议 `gimbal move ...;`，受下位机限制：
    - `pitch` ∈ [-55, 55]°；
    - `yaw` ∈ [-55, 55]°；
    - `vpitch`/`vyaw` ∈ [0, 540]°/s；
  - 若角度或速度超出范围，抛 `ValueError`；
  - 不建议在高层直接调用，应通过封装后的 `rotate_gimbal` 使用。

- `_move_gimbal_absolute(pitch, yaw, vpitch, vyaw)`（绝对角度，非阻塞）
  - 对应协议 `gimbal moveto ...;`，硬件限制更严格：
    - `pitch` ∈ [-25, 30]°；
    - `yaw` ∈ [-250, 250]°；
    - 速度范围同上；
  - 同样只建议作为封装实现，不直接在业务代码中调用。

### 5.2 高层主操作函数

- `set_gimbal_speed(pitch: float, yaw: float, delay: bool = True) -> None`
  - 对应协议：`gimbal speed p <pitch> y <yaw>;`；
  - 设计为“巡航”函数：在非零速度下，会根据 `360 / max(|pitch|, |yaw|)` 估算一圈时间并 `sleep`，
    巡航完成后自动调用 `set_gimbal_recenter()` 回中；
  - 主要用于测试/演示，不建议在自瞄等实时控制中频繁使用。

- `set_gimbal_suspend() / set_gimbal_resume()`
  - 对应协议：`gimbal suspend;` / `gimbal resume;`。

- `set_gimbal_recenter(delay: bool = True)`
  - 由于官方 `gimbal recenter;` 在竖直方向上不可靠，这里通过 `_move_gimbal_absolute(0, 0, 180, 180)` 实现回中；
  - 若 `delay=True`，会按照“最大偏移 55°、速度 180°/s”估算回中时间并 `sleep`。

- `rotate_gimbal(pitch=None, yaw=None, vpitch=None, vyaw=None, delay=True)`
  - 这是**推荐的主操作函数**（相对角度模式，支持滑环 360° 无限旋转）：
    - 对 pitch 做范围校验：[-55, 55]°，超出会裁剪并在执行后抛异常提醒；
    - 对 yaw 进行归一化：使用 `[-180, 180)` 范围选择最短旋转路径；
    - 将大角度拆分为多次 ≤50° 的步进，并在每步后按速度计算等待时间；
  - 如果 `delay=True`，整个函数会在所有步进完成后才返回，因此非常适合在独立线程中调用
    （例如在技能线程内进行大角度扫描）。

- `rotate_gimbal_absolute(pitch=None, yaw=None, vpitch=None, vyaw=None, delay=True)`
  - 以**绝对角度**为目标进行控制，结合下位机绝对角度限制和相对分步逻辑：
    - 在 `[-25, 30]°` / `[-250, 250]°` 以内直接发送 moveto 指令；
    - 超出范围时将超额部分拆成相对角度步进，通过 `_move_gimbal` 实现；
  - 适用于需要精确指向某个绝对方向的场景，但要注意分步相对控制可能引入累积误差。

> 关键警告：
> - 俯仰轴（pitch）不能无限旋转，任何超过机械极限的请求都会被裁剪并抛异常提醒；
> - 偏航轴（yaw）在安装滑环后可以实现 360° 连续旋转，但仍受单次指令 ±55° 的限制；
> - 大角度操作通常是阻塞的，务必在独立线程中使用（例如技能线程）。

---

## 6. 发射器控制（`blaster.py`）

文件：`src/bot/blaster.py`

- `set_blaster_bead(num: int) -> None`
  - 对应协议：`blaster bead <num>;`；
  - `num` 范围 [1, 5]，超出抛 `ValueError`；
  - 建议在技能或测试代码中明确设置发射量，而不要在多个位置硬编码数字。

- `blaster_fire() -> None`
  - 对应协议：`blaster fire;`；
  - 无参数，单次触发按当前设定发射量射击。

> 安全建议：未来可以在更高层封装“冷却时间”“最大连发数”等逻辑，避免无节制触发发射指令。

---

## 7. 赛事输入与按键数据（`game_msg.py`）

文件：`src/bot/game_msg.py`

- `game_msg_on() / game_msg_off()`
  - 对应协议：`game msg on;` / `game msg off;`，控制是否接收赛事数据推送；
- `game_msg_process(data: str) -> GameMsgDictType`
  - 将如 `game msg push [0, 6, 1, 0, 0, 255, 1, 199];` 的原始字符串解析为结构化字典：
    - `mouse_press`, `mouse_x`, `mouse_y`, `key_num`, `keys` 等；
  - 当前仅对按键编码使用 `chr(int(x) - 80)` 映射为小写字母，
    这一逻辑在注释中有详细推导说明，并被标记为待确认/可扩展的 TODO。

技能系统（`skill/*`）可以基于 `keys` 字段来触发对应技能，实现「比赛输入 → 高层行为」的链路。

---

## 8. 使用建议与典型调用顺序

在一个完整的硬件控制流程中，推荐的典型顺序是：

1. 打开串口并验证下位机：
   - 调用 `bot.conn.open_serial()`，检查返回值；
2. 进入 SDK 模式：
   - 调用 `bot.sdk.enter_sdk_mode()`；
3. 设置机器人模式与初始姿态：
   - `bot.robot.set_robot_mode("free")`；
   - 必要时调用 `bot.gimbal.set_gimbal_recenter()` 回中；
4. 启动 REPL 或主控制循环：
   - 在循环中调用 `chassis`, `gimbal`, `blaster` 等模块提供的高层 API；
   - 技能系统（`skill/*`）与自瞄（`aimassistant/*`）使用这些 API 组合出更复杂行为；
5. 程序结束或需要安全退出时：
   - 调用 `bot.sdk.exit_sdk_mode()`；
   - 调用 `bot.conn.close_serial()` 关闭串口。

---

## 9. 推荐阅读与后续扩展

- `docs/reference/sdk_protocol_api_document.md`
  - 了解所有底层命令的完整参数与返回值定义；
- `docs/intro/skill_intro.md`
  - 了解技能系统如何基于 `bot/*` 提供的 API 组合出高层行为；
- `docs/guide/repl.md`
  - 学习如何通过 REPL 快速验证某个底层控制函数（例如测试云台角度、底盘速度、发射器行为）；
- 未来可补充的文档：
  - `docs/journey/uart_communication_journey.md`：记录串口与 SDK 交互的踩坑历程与性能优化；
  - `docs/guide/hardware_safety.md`：集中说明云台/底盘/发射器的安全使用注意事项与案例。

> 在添加新的硬件控制函数或调整现有参数范围时，建议同步更新本 intro 与 SDK reference，
> 并通过 REPL 在真实硬件上验证行为，确保参数校验与实际物理限制一致。