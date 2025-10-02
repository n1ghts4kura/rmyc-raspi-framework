# Copilot Instructions for RMYC Raspi Framework

## 项目概览
本项目是基于 Raspberry Pi 的 DJI RoboMaster S1/EP 机器人控制框架，用于机甲大师空地协同对抗赛（RMYC）。采用 Python 开发，通过 UART 串口与机器人通信，支持技能系统、视觉自瞄、键鼠事件绑定等功能。

### ⚠️ 重要说明
- **辅助开发文档**: 请参考 `documents/` 目录下的文档，这些文档包含了项目的设计理念、使用说明和开发指南，有助于理解代码结构和功能实现。
- **开发环境 vs 运行环境**：如果检测到用户在 Windows 环境下编辑代码，这仅用于开发和调试。**所有代码最终都在 Raspberry Pi (Linux) 上运行**。不要考虑 Windows 兼容性问题，串口路径、权限设置等均以 Linux 为准（如 `/dev/ttyUSB0`）。
- **aimassistant/ 模块**：该目录内容正在开发中，暂时内容较少属于正常情况。
- **test_*.py 文件**：这些是早期测试文件，待框架体系完善后会被移除，不需要维护或扩展这些测试。

### 要求
- 编码要求: **准确** 、**简洁**、**高效**、**符合 Python 习惯用法**
- 文档要求: **清晰** 、**完整**、**易懂**
- 测试要求: **所有代码必须在 Linux/Raspberry Pi 上可运行**
- **编码记录**要求：每次操作，无论是否进行实质性代码增删，**都必须** 在 `documents/` 目录下维护`*_journey.md`文档 用于记录思考过程和决策依据。如果感知到编码迈向了另一个阶段（如从调试到重构），**必须** 创建新的`*_journey.md`文档。如果不确定，**必须** 创建新的文档。 每次编辑代码后，**必须** 同步维护`*journey.md`文档，确保文档内容是最新的最符合项目当前状态的。
- **多提问**: 如果编码过程中遇到不确定的问题 / 用户的回答与上下文不符合，**必须** 主动提问以获取更多上下文
- **必须** 要有显式 **思考过程**，避免盲目生成代码

## 核心架构与数据流

### 三层架构
1. **硬件抽象层** (`src/bot/`)：封装串口通信与机器人硬件控制
2. **业务逻辑层** (`src/skill/`, `src/aimassitant/`)：技能管理、视觉识别
3. **应用层** (`src/main.py`, `src/repl.py`)：主循环调度、调试工具

### 关键数据流
```
键鼠事件 → 串口 → game_msg_process() → SkillManager.change_skill_state() → 技能执行
                ↓
          硬件控制命令 (chassis/gimbal/blaster)
```

## 串口通信机制（重要）

### 命令格式
- **发送**：所有命令以分号结尾，如 `chassis speed x 1.0 y 0 z 0;`
- **接收**：使用队列机制分离"原始行"和"命令"（分号分隔）
  - `get_serial_line_nowait()`：获取原始行
  - `get_serial_command_nowait()`：获取分号分隔的命令

### 后台线程模型
- `start_serial_worker()` 启动后台接收线程
- 双队列设计：`_rx_queue`（行级）、`_cmd_queue`（命令级）
- 空闲超时机制：超过 0.1s 无数据时，缓冲区作为一帧返回

### 编码注意事项
- 串口操作需通过 `serial_conn_lock` 保护
- **部署目标**：代码最终在 Raspberry Pi (Linux) 上运行，串口路径使用 `/dev/ttyUSB0`
- 调试时优先使用 `src/repl.py` 查看实时串口交互

## 技能系统核心模式

### 技能定义规范
```python
from skill.base_skill import BaseSkill

def my_action(skill: BaseSkill):
    # 技能逻辑：通过 skill.enabled 检查状态
    # 异常处理：使用 skill.set_errored(True) 标记错误
    pass

skill = BaseSkill(
    binding_key="w",  # 必须小写！键值自动转换
    invoke_func=my_action,
    name="技能名称"
)
```

### 状态切换机制
- 按键首次触发 → `async_invoke()` → 启动新线程执行
- 再次按下同键 → `async_cancel()` → 等待线程结束（5s 超时）
- **互斥保证**：`SkillManager` 确保键位唯一，但不限制同时运行的技能数量

### 实际案例
参考 `src/skill/example_skill.py`：展示延时执行 + 硬件调用模式

## 硬件控制 API 约定

### 参数范围验证（严格）
所有 `bot/` 模块函数在参数超出范围时抛出 `ValueError`：
- **底盘速度**：`chassis.set_chassis_speed_3d(x, y, z)` → x/y ∈ [-3.5, 3.5] m/s，z ∈ [-600, 600] °/s
- **云台角度**：`gimbal.move_gimbal(pitch, yaw, ...)` → 相对角度 ∈ [-55, 55]°
- **发射数量**：`blaster.set_blaster_bead(num)` → num ∈ [1, 5]

### SDK 模式切换
- `enter_sdk_mode()`：主程序启动后调用，进入可编程模式
- `exit_sdk_mode()`：异常退出或关闭时必须调用，释放控制权

### 示例：云台回中实现
```python
# 优先使用封装好的回中函数
from bot.gimbal import set_gimbal_recenter
set_gimbal_recenter()  # 内部调用 move_gimbal_absolute(0, 0, 90, 90)
```

## 游戏消息解析（game_msg）

### 数据结构
`game_msg_process()` 返回 `GameMsgDictType`，包含：
- `mouse_press`：鼠标按键状态（位掩码）
- `keys`：按下的键盘按键列表（小写字母，最多 3 个）
- **键值映射**：接收数字减 80 得 ASCII 码，如 `199 → 'w'`

### 主循环集成
```python
line = get_serial_command_nowait()
if line.startswith("game msg push"):
    msg_dict = game_msg_process(line)
    for key in msg_dict.get("keys", []):
        skill_manager.change_skill_state(key)
```

## 视觉识别架构（recognizer.py）

### 双线程设计
- **采集线程**：持续从摄像头读取帧
- **推理线程**：异步运行 YOLO 检测，结果缓存至 `latest_result`
- **优势**：解耦 I/O 与计算，避免推理阻塞采集

### 使用模式
```python
from recognizer import Recognizer
rec = Recognizer(model_path="model/yolov8n.pt")
rec.start()
# 主循环中
result = rec.get_latest_result()  # 非阻塞获取最新检测
rec.imshow()  # 调试用：显示标注后的图像
```

## 日志系统（logger.py）

### 全局导入规范
```python
import logger as LOG  # 统一别名

LOG.debug("调试信息")   # 仅 DEBUG_MODE=True 时输出
LOG.info("状态更新")
LOG.warning("警告")
LOG.error("错误")
LOG.exception("异常")  # 自动附加堆栈
```

### 彩色输出
- INFO：绿色 | WARNING：黄色 | ERROR：红色 | DEBUG：青色
- REPL 中通过 `prompt_toolkit` 实现彩色日志面板

## 开发工作流

### 环境搭建（Windows PowerShell）
```powershell
python -m venv .\venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 调试流程
1. **串口测试**：`python src/repl.py` → 发送 `command;` 检查响应
2. **技能验证**：主程序中绑定测试键，观察日志输出
3. **视觉调试**：调用 `Recognizer.imshow()` 查看检测结果

### 关于测试文件
- `test_*.py` 是早期测试代码，待体系完善后会被移除
- 不建议在这些文件上投入维护精力
- 新功能测试应集成到技能系统或 REPL 中验证

## 编码约定

### 命名规范
- 函数：`[动词]_[名词]`，如 `set_chassis_speed`、`move_gimbal`
- 变量：小写下划线，如 `serial_conn`、`_rx_queue`
- 私有变量/函数：单下划线前缀 `_rx_buf`

### 类型注解（必需）
所有公共函数必须提供类型提示，使用 `typing` 模块：
```python
def chassis_move(distance_x: float, speed_xy: float | None) -> None:
```

### 文档字符串
硬件控制函数必须包含参数范围说明：
```python
"""
Args:
    pitch (float): 云台俯仰角度，范围[-55, 55] (°)
Raises:
    ValueError: 如果参数超出范围
"""
```

## 文档维护规则

### documents/ 结构
- **主题隔离**：每个文档专注单一主题（如 `aimassistant_intro_for_ai.md`）
- **AI 协作**：开发前后更新进度文档，辅助后续 AI 理解上下文
- **命名规范**：`[模块]_[主题]_for_ai.md`

### 提交前检查清单
- [ ] 更新相关 `documents/` 文档
- [ ] 通过 REPL 或主程序验证功能正常
- [ ] 确认日志输出无异常
- [ ] 硬件控制代码已添加参数范围注释
- [ ] 确保代码在 Linux/Raspberry Pi 环境下可运行

## 常见问题与陷阱

### 1. 技能按键不触发
- 检查键值是否小写：`BaseSkill(binding_key="W")` → 应为 `"w"`
- 确认 `game_msg_process()` 的键值映射逻辑（数字 - 80）

### 2. 串口无响应
- Windows：检查 COM 端口号，使用设备管理器确认
- Linux：执行 `sudo chmod 777 /dev/ttyUSB0` 赋予权限
- 确认调用 `start_serial_worker()` 启动后台线程
- **注意**：Windows 仅用于开发调试，部署时在 Raspberry Pi 上使用 `/dev/ttyUSB0`

### 3. 云台/底盘不动
- 验证是否调用 `enter_sdk_mode()`
- 检查参数是否在有效范围内（会抛出 `ValueError`）
- 使用 REPL 发送原始命令测试硬件响应

### 4. 视觉识别帧率低
- 检查 `rec.get_fps_info()` 输出
- 降低模型复杂度或图像分辨率
- 确认双线程正常运行（采集与推理分离）

## 扩展指南

### 添加新技能
1. 在 `src/skill/` 创建文件，参考 `example_skill.py`
2. 在 `main.py` 中 `skill_manager.add_skill(new_skill)`
3. 测试按键触发与日志输出

### 添加新硬件模块
1. 在 `src/bot/` 创建模块，导入 `conn`
2. 函数签名包含参数范围验证
3. 在 `__all__` 中导出公共 API
4. 更新 `documents/` 中的硬件说明

## 参考资料
- 详细架构说明：`documents/general_intro_for_ai.md`
- 自瞄系统设计：`documents/aimassistant_intro_for_ai.md`
- REPL 工具使用：`documents/repl.md`
