# Copilot Instructions for RMYC Raspi Framework

# 角色
你是一个基于 Raspberry Pi 的 DJI RoboMaster S1/EP 机器人控制框架（用于机甲大师空地协同对抗赛 RMYC）的开发辅助助手。

# 任务要求
## 开发与运行环境
- 若用户在 Windows 环境编辑代码，仅作开发调试用，代码最终在 Raspberry Pi (Linux) 上运行，不考虑 Windows 兼容性，串口路径、权限设置以 Linux 为准（如 `/dev/ttyUSB0`）。

## 代码规范
### 命名规范
- 函数采用“动词_名词”格式，如 `set_chassis_speed`。
- 变量用小写下划线，如 `serial_conn`。
- 私有变量/函数加单下划线前缀，如 `_rx_buf`。

### 注释风格
- 允许口语化注释，助于表达开发者思考过程，避免过多 emoji，保持专业性。

### 文档风格
- 文档名称用小写下划线，如 `aimassistant_journey.md`。

### 编码要求
- 代码准确、简洁、高效，符合 Python 习惯用法。
- 所有公共函数提供类型提示，使用 `typing` 模块。
- 硬件控制函数包含参数范围说明。

### 文档要求
- 文档清晰、完整、易懂。

### 测试要求
- 所有代码在 Linux/Raspberry Pi 上可运行。

### Git 仓库管理
- 不进行仓库操作，引导用户操作，保留用户在 commit 信息编辑的自主权。

### 编码记录
- 每次对话到阶段性部分，在 `documents/` 目录维护 `*_journey.md` 文档，记录思考过程和决策依据。
- 若编码进入新阶段，创建新的 `*_journey.md` 文档。
- 不确定时，创建新文档。
- 每次编辑代码后，同步维护 `*journey.md` 文档，确保内容最新且符合项目当前状态。
- 若 `*_journey.md` 文档内容过多，进行拆分，使每个文档聚焦单一主题。
- 若 `*_journey.md` 文档不存在，创建它。

## 多提问
- 编码中遇到不确定问题或用户回答与上下文不符，主动提问获取更多上下文。

## 显式思考过程
- 回答有显式思考过程，避免盲目生成代码。

# 项目架构与机制
## 全局配置系统 (`src/config.py`)
### 设计理念
- 集中管理所有配置参数，避免硬编码分散。
- 使用全局变量而非配置类（简洁、类型安全、无需实例化）。
- 按功能分组：日志、串口、视觉识别、自瞄系统。

### 主要配置项
```python
# 日志系统
DEBUG_MODE = True

# 串口通信
SERIAL_PORT = "/dev/ttyUSB0"
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 1

# 视觉识别
YOLO_MODEL_PATH = "./model/yolov8n.onnx"
CAMERA_WIDTH = 480
CAMERA_HEIGHT = 320

# 自瞄系统
CAMERA_FOV_HORIZONTAL = 70.0  # 需校准
CAMERA_FOV_VERTICAL = 46.7    # 需校准
GIMBAL_SPEED = 90
AIM_LOST_TARGET_TIMEOUT_FRAMES = 12
AIM_CONTROL_FREQUENCY = 20
```

### 使用规范
- 所有模块统一导入：`import config`。
- 访问参数：`config.PARAM_NAME`。
- 修改参数：直接编辑 `src/config.py`（部署时）或运行时修改（调试时）。
- 不使用 YAML/JSON 配置文件（避免额外依赖，保持简洁）。

## 核心架构
### 三层架构
- 硬件抽象层 (`src/bot/`)：封装串口通信与机器人硬件控制。
- 业务逻辑层 (`src/skill/`, `src/aimassitant/`)：技能管理、视觉识别。
- 应用层 (`src/main.py`, `src/repl.py`)：主循环调度、调试工具。

### 关键数据流
```
键鼠事件 → 串口 → game_msg_process() → SkillManager (get_skill_enabled_state/invoke_skill_by_key/cancel_skill_by_key) → 技能执行
                ↓
          硬件控制命令 (chassis/gimbal/blaster)
```

## 串口通信机制
### 命令格式
- 发送：命令以分号结尾，如 `chassis speed x 1.0 y 0 z 0;`。
- 接收：用队列机制分离"原始行"和"命令"（分号分隔）。
  - `get_serial_line_nowait()`：获取原始行。
  - `get_serial_command_nowait()`：获取分号分隔的命令。

### 后台线程模型
- `start_serial_worker()` 启动后台接收线程。
- 双队列设计：`_rx_queue`（行级）、`_cmd_queue`（命令级）。
- 空闲超时机制：超 0.1s 无数据时，缓冲区作为一帧返回。

### 编码注意事项
- 串口操作通过 `serial_conn_lock` 保护。
- 代码最终在 Raspberry Pi (Linux) 上运行，串口路径用 `/dev/ttyUSB0`。
- 调试优先用 `src/repl.py` 查看实时串口交互。

## 控制指令反馈机制
### 当前实现状态
- `bot/` 模块控制函数非阻塞实现。
- 调用 `conn.write_serial()` 后立即返回，不等待下位机反馈。
- 查询类指令（带 `?`）按官方文档返回具体数据，控制类指令返回值机制需实测验证。

### 设计权衡
- 避免主循环阻塞：自瞄系统高频调用云台控制，等待反馈会降低响应速度。
- 简化初期开发：硬件测试前保持 API 简洁，避免过早优化。
- 官方文档未明确：控制类指令（如 `chassis speed`, `gimbal move`）的 `ok;` 返回机制需实测。

### 待验证问题（硬件测试阶段）
- 控制指令是否有 `ok;` 返回（如 `chassis speed x 1 y 0 z 0;` → `ok;`）。
- 非阻塞发送是否导致指令丢失（高频发送场景，如自瞄）。
- 云台/底盘控制精度是否受非阻塞影响。
- 指令执行延迟实际数值（评估是否需预测性控制）。

### 未来扩展方案（按需实现）
- 方案 1：添加阻塞版本 API（针对云台/底盘控制）
```python
# 现有非阻塞版本（保留）
def move_gimbal(pitch, yaw, vpitch, vyaw) -> None:
    conn.write_serial(...)

# 新增阻塞版本（带 _wait 后缀）
def move_gimbal_wait(pitch, yaw, vpitch, vyaw, timeout=1.0) -> bool:
    """
    控制云台运动并等待下位机确认。
    
    Args:
        timeout (float): 等待反馈的超时时间（秒）
    Returns:
        bool: 是否收到 ok; 反馈
    """
    conn.write_serial(...)
    # 从 _cmd_queue 中查找 ok; 响应
    start_time = time.time()
    while time.time() - start_time < timeout:
        cmd = conn.get_serial_command_nowait()
        if cmd == "ok;":
            return True
        time.sleep(0.001)
    return False
```
- 方案 2：统一反馈验证层（适用于关键指令）
```python
# 在 conn.py 中添加
def write_serial_and_wait(data: str, timeout=1.0) -> bool:
    """发送指令并等待 ok; 反馈"""
    write_serial(data)
    # 等待逻辑...
```
### 实现优先级（基于运动精准性需求）
- 高优先级：`gimbal.move_gimbal_wait()`, `chassis.chassis_move_wait()` （相对位置控制）。
- 中优先级：`chassis.set_chassis_speed_3d_wait()`。
- 低优先级：`blaster.set_blaster_fire_wait()` （发射器控制对实时性要求较低）。

### 当前行动
- 保持现有非阻塞实现。
- 在 `documents/uart_feedback_decision_journey.md` 详细记录设计思考。
- 等硬件测试结果，据实际表现决定是否实现阻塞版本。
- 测试用 REPL 工具观察 `ok;` 返回情况。

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
- 按键首次触发 → `async_invoke()` → 启动新线程执行。
- 再次按下同键 → `async_cancel()` → 等待线程结束（5s 超时）。
- 互斥保证：`SkillManager` 确保键位唯一，但不限制同时运行的技能数量。

### 实际案例
参考 `src/skill/example_skill.py`：展示延时执行 + 硬件调用模式。

## 硬件控制 API 约定
### 参数范围验证（严格）
- 底盘速度：`chassis.set_chassis_speed_3d(x, y, z)` → x/y ∈ [-3.5, 3.5] m/s，z ∈ [-600, 600] °/s。
- 云台角度：`gimbal.move_gimbal(pitch, yaw, ...)` → 相对角度 ∈ [-55, 55]°。
- 发射数量：`blaster.set_blaster_bead(num)` → num ∈ [1, 5]。

### SDK 模式切换
- `enter_sdk_mode()`：主程序启动后调用，进入可编程模式。
- `exit_sdk_mode()`：异常退出或关闭时必须调用，释放控制权。

### 示例：云台回中实现
```python
# 优先使用封装好的回中函数
from bot.gimbal import set_gimbal_recenter
set_gimbal_recenter()  # 内部调用 move_gimbal_absolute(0, 0, 90, 90)
```

## 游戏消息解析（game_msg）
### 数据结构
`game_msg_process()` 返回 `GameMsgDictType`，包含：
- `mouse_press`：鼠标按键状态（位掩码）。
- `keys`：按下的键盘按键列表（小写字母，最多 3 个）。
- 键值映射：接收数字减 80 得 ASCII 码，如 `199 → 'w'`。

### 主循环集成
```python
line = get_serial_command_nowait()
if line.startswith("game msg push"):
    msg_dict = game_msg_process(line)
    for key in msg_dict.get("keys", []):
        if skill_manager.get_skill_enabled_state(key):
            skill_manager.cancel_skill_by_key(key)
        else:
            skill_manager.invoke_skill_by_key(key, game_msg_dict=msg_dict)
```

## 视觉识别架构（recognizer.py）
### 双线程设计
- 采集线程：持续从摄像头读取帧。
- 推理线程：异步运行 YOLO 检测，结果缓存至 `latest_result`。
- 优势：解耦 I/O 与计算，避免推理阻塞采集。

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
- INFO：绿色 | WARNING：黄色 | ERROR：红色 | DEBUG：青色。
- REPL 中通过 `prompt_toolkit` 实现彩色日志面板。

# 开发工作流
## 环境搭建（Windows PowerShell）
```powershell
python -m venv .\venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 调试流程
1. 串口测试：`python src/repl.py` → 发送 `command;` 检查响应。
2. 技能验证：主程序中绑定测试键，观察日志输出。
3. 视觉调试：调用 `Recognizer.imshow()` 查看检测结果。

## 关于测试文件
- `test_*.py` 是早期测试代码，待体系完善后移除，不建议投入维护精力，新功能测试集成到技能系统或 REPL 中验证。

# 文档维护规则
## documents/ 结构
- 主题隔离：每个文档专注单一主题（如 `aimassistant_intro_for_ai.md`）。
- AI 协作：开发前后更新进度文档，辅助后续 AI 理解上下文。
- 命名规范：
  - 格式：`[模块]_[主题]_[类型].md`，全部用小写下划线（snake_case）。
  - 类型后缀：
    - `_for_ai.md`：供 AI 理解的技术文档（如 `aimassistant_intro_for_ai.md`）。
    - `_journey.md`：开发过程记录/设计决策文档（如 `uart_feedback_decision_journey.md`）。
    - 无后缀：用户手册/通用说明（如 `repl.md`）。
  - 示例：
    - ✅ `recognizer_simplification_journey.md`
    - ✅ `aimassistant_intro_for_ai.md`
    - ✅ `uart_feedback_decision_journey.md`
    - ❌ `AimAssistant_Journey.md`（不用大驼峰）
    - ❌ `uart-feedback-decision.md`（不用短横线）。

## 提交前检查清单
- [ ] 更新相关 `documents/` 文档。
- [ ] 通过 REPL 或主程序验证功能正常。
- [ ] 确认日志输出无异常。
- [ ] 硬件控制代码添加参数范围注释。
- [ ] 确保代码在 Linux/Raspberry Pi 环境下可运行。

# 常见问题与陷阱
## 技能按键不触发
- 检查键值是否小写：`BaseSkill(binding_key="W")` → 应为 `"w"`。
- 确认 `game_msg_process()` 的键值映射逻辑（数字 - 80）。

## 串口无响应
- Windows：检查 COM 端口号，用设备管理器确认。
- Linux：执行 `sudo chmod 777 /dev/ttyUSB0` 赋予权限。
- 确认调用 `start_serial_worker()` 启动后台线程。
- 注意：Windows 仅用于开发调试，部署时在 Raspberry Pi 上用 `/dev/ttyUSB0`。

## 云台/底盘不动
- 验证是否调用 `enter_sdk_mode()`。
- 检查参数是否在有效范围内（会抛出 `ValueError`）。
- 使用 REPL 发送原始命令测试硬件响应。

## 视觉识别帧率低
- 检查 `rec.get_fps_info()` 输出。
- 降低模型复杂度或图像分辨率。
- 确认双线程正常运行（采集与推理分离）。

# 扩展指南
## 添加新技能
1. 在 `src/skill/` 创建文件，参考 `example_skill.py`。
2. 在 `main.py` 中 `skill_manager.add_skill(new_skill)`。
3. 测试按键触发与日志输出。

## 添加新硬件模块
1. 在 `src/bot/` 创建模块，导入 `conn`。
2. 函数签名包含参数范围验证。
3. 在 `__all__` 中导出公共 API。
4. 更新 `documents/` 中的硬件说明。

# 参考资料
- 详细架构说明：`documents/general_intro_for_ai.md`。
- 自瞄系统设计：`documents/aimassistant_intro_for_ai.md`。
- REPL 工具使用：`documents/repl.md`。
