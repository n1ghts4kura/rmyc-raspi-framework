## 启动

以下命令**只能在目标运行环境（树莓派 Linux）上执行**，开发机（Windows）仅用于编辑代码与同步到仓库，不运行任何项目代码：

```bash
# 在树莓派上，进入项目根目录后：

# 如使用虚拟环境（可选）
source ./venv/bin/activate

# 启动 REPL 工具
python src/repl.py
```
- 颜色区分：更直观地区分发送/接收/告警
- 输入区固定在底部，回车即发；不阻塞接收显示
- 后台队列式接收线程，高频数据也流畅；自动贴近底部分隔线显示

注意：请根据你的设备修改 `src/bot/conn.py` 中的 `_device_address`（如 `/dev/ttyUSB0`、`/dev/ttyACM0`）。

## 启动

在项目根目录运行（根据你的环境选择其一）：

```bash
# Linux / macOS（如果使用 venv）
source ./venv/bin/activate
python src/repl.py

# Windows PowerShell（如果使用 venv）
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python src/repl.py

# 已全局安装依赖时（任意平台）
python src/repl.py
```

# 背景与适用范围

- 工具位置：`src/repl.py`，基于 `asyncio` 与 `prompt_toolkit` 封装的串口调试台，主要服务于树莓派上的 RoboMaster SDK 调试场景。
- 目标读者：需要实时观测串口交互、调试键鼠透传或监控后台线程状态的算法、嵌入式与运维成员。
- 准入条件：确保串口地址配置正确（默认 `/dev/ttyUSB0`），安装 `prompt_toolkit`、`pyserial` 等依赖，并遵循 `docs/principles.md` 中的工具使用规范。

## 核心内容

### 功能概览

- 界面分区：输出区占屏幕约 80%，底部输入区 20%，中间使用分隔线保持布局稳定。
- 输出特征：显示发送与接收数据，附 24 小时制毫秒级时间戳，颜色区分发送/接收/告警。
- 输入交互：底部输入框不阻塞接收线程，回车即发送，历史记录支持滚动阅览。
- 后台能力：独立线程负责串口读取，结合队列缓冲防止高频数据丢失；渲染节流约 16ms。

### 颜色与标签约定

- `[SEND]` 行采用亮绿色，表示用户主动发送的命令。
- `[RECV]` 行使用青色区分机器人回传的数据。
- `[WARN]` 行使用橙色提醒连接或权限异常。
- 时间戳为浅灰色，有助于定位事件顺序；终端若不支持 TrueColor 将自动降级。

### 内置命令与快捷键

- `:q` / `:quit` / `:exit` / `quit` / `exit`：安全退出；推荐在关闭串口前先执行。
- `:help` / `:h` / `?`：列出所有内置命令。
- `:eol [crlf|lf|cr|none]`：配置发送行结尾。默认 `none` 以兼容 DJI 分号语法。
- `Ctrl+C`：强制退出（会触发 KeyboardInterrupt，由主循环处理）。

### 行结尾配置策略

- DJI RoboMaster 明文协议以分号 `;` 作为指令分隔符，因此默认不附加换行；若错误设为 `crlf`，会导致多余的回车字符破坏命令结构。
- 连接其他需要换行的串口设备时，可临时切换到 `lf` 或 `crlf`，任务完成后执行 `:eol none` 恢复。

### 设计细节

- `start_serial_worker()` 启动后台线程，持续读取串口并写入队列。
- `read_serial_nonblock()` 以 CR/LF 检测帧边界，如超时则将缓冲区残留作为完整帧输出，避免阻塞。
- 指令队列与原始行队列分离，保障以分号结尾的命令能够被 `get_serial_command_nowait()` 按顺序消费。
- 输出历史缓存 10,000 行，渲染时按当前窗口高度裁减，保持视图贴近分隔线。

### 常见故障排查

1. **无串口输出或无法连接**：核对 `_device_address` 与硬件一致，必要时执行 `sudo chmod 777 /dev/ttyUSB0`；确认波特率 115200 匹配。
2. **发送失败告警**：`[WARN]` 表示串口句柄失效或断开，请重新插拔设备并重启 REPL。
3. **IDE 报模块缺失**：VS Code 如未指向正确虚拟环境，请切换解释器或重新安装依赖。
4. **颜色异常**：终端不支持 TrueColor，可改用支持更好的终端或接受退化显示。

### 拓展方向

- 可以添加命令补全、历史检索、日志持久化与 HEX/ASCII/JSON 视图等功能。
- 若需要与自动化测试联动，可在后台线程中写入文件或暴露 WebSocket 接口。

## 操作步骤

1. **环境准备**（在树莓派上完成）：
    - （可选）创建并激活虚拟环境，安装项目依赖；
    - 修改 `src/bot/conn.py` 中的 `_device_address` 以匹配实际串口设备（如 `/dev/ttyUSB0`）；
    - 建议在使用前快速阅读 `docs/intro/bot_intro.md`，了解串口与 SDK 模式的整体行为。
2. **启动命令**（在树莓派上执行）：

    ```bash
    # 如使用虚拟环境
    source venv/bin/activate

    # 启动 REPL 工具
    python src/repl.py
    ```
3. **串口调试**：在底部输入框中发送如 `command;`、`gimbal move p 0 y 0;` 等命令，观察上方 `[RECV]` 反馈。
4. **调整行结尾**：调试非 DJI 设备时使用 `:eol lf` 或 `:eol crlf`，完成后恢复 `:eol none`。
5. **退出流程**：依次执行 `:quit` 或 `Ctrl+C`，确保后台线程完成收尾，再关闭终端。

## 验证与状态

- `status: active` 表示该工具为日常调试标配组件；最近一次人工复核为 2025-10-18。
- 当前版本在 macOS 与树莓派 Linux 下通过基础串口测试；若在实际 RoboMaster 硬件上验证到新的行为差异，建议：
    - 在相关 journey 文档（例如 `docs/journey/performance_journey.md` 或未来的 `uart_communication_journey.md`）中记录；
    - 同步更新本指南的“常见故障排查”章节。
- 后续若扩展日志持久化或命令补全，需要更新本章，并根据需要在 `docs/index.md` 或 `docs/status.md` 中标注变更。

## 附录与引用

- 依赖模块：`prompt_toolkit`、`pyserial`
- 相关代码：`src/repl.py`、`src/bot/conn.py`
- 推荐阅读：
    - `docs/intro/bot_intro.md`：了解串口、SDK 模式与底盘/云台控制的整体结构；
    - `docs/principles.md`：项目整体约定与工具使用规范；
    - `docs/journey/performance_journey.md`：与串口与性能相关的历史经验。

---
若在调试过程中遇到与日志、串口协议相关的新问题，**建议**：

1. 在合适的 journey 文档中记录现象、原因与解决方案（例如新增 `docs/journey/uart_communication_journey.md` 或补充到现有性能相关 journey 中）。
2. 视问题影响范围，按需更新本指南的“常见故障排查”章节。

这不是硬性 24 小时内必须完成的流程要求，但鼓励在问题解决后尽快同步文档，以便后续排查和协作。

