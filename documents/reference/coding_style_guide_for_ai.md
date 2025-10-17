# 编码风格指南（供 AI 参考）

## 文档目标
本文档为 AI 助手提供明确的编码风格参考，确保生成的代码与现有项目风格保持一致。

---

## 核心原则

### 设计理念
1. **简洁优于复杂**：优先选择简单直接的实现，避免过度设计
2. **类型安全**：利用类型提示提高代码可靠性，特别是硬件控制代码
3. **可维护性**：通过注释和命名表达设计意图，3 个月后能快速理解
4. **Python 惯用法**：遵循 PEP 8，使用现代 Python 特性（3.10+）

### 适用范围
- 所有 `src/` 目录下的 Python 代码
- 硬件控制代码（`src/bot/`）有更严格的要求
- 工具脚本（`tools/`）可适当放宽

---

## 1. 命名规范

### 1.1 函数命名
- **格式**：`动词_名词`（snake_case）
- **原则**：函数名应清晰表达"做什么"

```python
# ✅ 推荐
def set_chassis_speed(x: float, y: float, z: float):
    ...

def get_latest_result() -> RecognizerResult | None:
    ...

def game_msg_process(line: str) -> GameMsgDictType:
    ...

# ❌ 不推荐
def chassisSpeed(x, y, z):  # 不使用驼峰命名
    ...

def process(line):  # 名称过于模糊
    ...
```

### 1.2 变量命名
- **格式**：snake_case
- **原则**：变量名应描述"是什么"，避免单字母变量（循环除外）

```python
# ✅ 推荐
serial_conn: s.Serial | None = None
lost_frames: int = 0
current_target_id: int = -1

# ❌ 不推荐
sc = None  # 名称过于简短
lostFrames = 0  # 不使用驼峰命名
x = -1  # 单字母变量（非循环）
```

### 1.3 私有成员
- **格式**：单下划线前缀 `_`
- **适用**：模块内部使用的函数、变量、类方法

```python
# ✅ 推荐
_rx_buf: str = ""
_cmd_queue: queue.Queue[str] = queue.Queue()

def _move_gimbal(pitch: float, yaw: float):
    """内部函数，不应被外部调用"""
    ...
```

### 1.4 类与类型别名
- **类名**：PascalCase
- **类型别名**：PascalCase + `Type` 后缀

```python
# ✅ 推荐
class BaseSkill:
    ...

class SkillManager:
    ...

# 类型别名
GameMsgDictType = TypedDict("GameMsgDictType", {
    "mouse_press": int,
    "keys": list[str]
})
```

### 1.5 常量
- **格式**：UPPER_SNAKE_CASE
- **位置**：模块顶部集中定义

```python
# ✅ 推荐
MAX_STEP_ANGLE: float = 55.0
_RX_IDLE_SEC: float = 0.1
DEFAULT_TIMEOUT: int = 5
```

---

## 2. 类型提示规范

### 2.1 语法选择
- **使用 Python 3.10+ 新语法**：`str | None`（而非 `Optional[str]`）
- **泛型简写**：`list[str]`（而非 `List[str]`）

```python
# ✅ 推荐（Python 3.10+）
def get_serial_line_nowait() -> str | None:
    ...

def get_latest_result() -> RecognizerResult | None:
    ...

targets: list[tuple[int, float, float, float, float]] = []

# ❌ 不推荐（旧语法）
from typing import Optional, List

def get_serial_line_nowait() -> Optional[str]:
    ...

targets: List[tuple] = []
```

### 2.2 覆盖范围
- **必须有类型提示**：
  - 所有公共函数的参数和返回值
  - 全局变量
  - 硬件控制函数（安全性要求）
  
- **可选类型提示**：
  - 局部变量（类型明显时）
  - 内部工具函数（逻辑简单时）

```python
# ✅ 推荐
# 公共 API 必须有完整类型提示
def move_gimbal(pitch: float, yaw: float, vpitch: int, vyaw: int) -> None:
    ...

# 全局变量有类型提示
serial_conn: s.Serial | None = None
_instance: Logger | None = None

# 局部变量类型明显，可省略
def process():
    result = get_latest_result()  # 类型明显
    if result is None:
        return
    ...
```

### 2.3 TypedDict 使用
- **适用场景**：定义复杂的字典结构
- **命名**：PascalCase + `Type` 后缀

```python
# ✅ 推荐
GameMsgDictType = TypedDict("GameMsgDictType", {
    "mouse_press": int,
    "keys": list[str]
})

def game_msg_process(line: str) -> GameMsgDictType:
    ...
```

---

## 3. 注释风格

### 3.1 文件头注释
- **格式**：简洁三行（文件名、作者、日期）
- **位置**：文件第一行

```python
# gimbal.py
# @author n1ghts4kura
# @date 2025/01/15
```

### 3.2 函数文档字符串
- **格式**：Google 风格
- **必须包含**：参数说明、返回值说明、异常说明（如有）
- **位置**：函数声明后、函数主体前（特别是职能复杂、应用场景多的函数）

```python
# ✅ 推荐
def move_gimbal(pitch: float, yaw: float, vpitch: int, vyaw: int) -> None:
    """
    控制云台运动（相对角度）。
    
    Args:
        pitch (float): 俯仰轴相对角度，范围 [-55, 55]
        yaw (float): 偏航轴相对角度，范围 [-55, 55]
        vpitch (int): 俯仰轴速度，范围 [0, 540]
        vyaw (int): 偏航轴速度，范围 [0, 540]
    
    Raises:
        ValueError: 参数超出范围
    """
    if not -55 <= pitch <= 55:
        raise ValueError(f"pitch {pitch} out of range [-55, 55]")
    ...
```

### 3.3 行内注释
- **口语化程度**：无标准限制，什么程度都可接受
- **适用场景**：
  - 简单逻辑：通过**明确的命名**解决，无需注释
  - 复杂逻辑：添加行尾注释说明

```python
# ✅ 推荐
# 简单逻辑：通过命名表达意图，无需注释
is_target_lost = lost_frames >= config.AIM_LOST_TARGET_TIMEOUT_FRAMES
if is_target_lost:
    ...

# 复杂逻辑：添加行尾注释
angle_normalized = (angle + 180) % 360 - 180  # 归一化到 [-180, 180)
step_angle = int(fov_horizontal * config.AIM_SEARCH_FOV_COVERAGE)  # 搜索步进占视野 70%

# 设计决策：详细说明"为什么"
# 使用双队列分离"原始行"和"命令"
# 原因：串口可能在命令中间换行，需要按分号分割
# 权衡：增加内存开销，但保证命令完整性
_rx_queue: queue.Queue[str] = queue.Queue()
_cmd_queue: queue.Queue[str] = queue.Queue()
```

### 3.4 TODO 注释
- **目的**：标记未完成的工作、待验证的问题
- **格式**：`# TODO: 描述`
- **生命周期**：每个版本发布前清理已完成的 TODO，长期未解决的移动到 issues 或文档

```python
# ✅ 推荐
# TODO: 需要硬件测试验证下位机返回值机制
# TODO: 搞清楚这个函数的返回值到底是什么

# ❌ 不推荐
# todo fix this  # 格式不统一，描述不清晰
```

### 3.5 作者署名
- **适用场景**：重要设计决策、复杂算法实现
- **格式**：`# *n1ghts4kura* 添加此功能`

```python
# ✅ 推荐
# *n1ghts4kura* 实现滑环 360° 旋转支持
def rotate_gimbal(yaw_delta: float):
    ...
```

### 3.6 Emoji 符号使用规则 ⚠️

#### 严格限制
- **只能**在代码注释和文档中出现
- **坚决不能**在命令行输出（print、logging）中出现
  - 原因：终端环境可能不支持 Emoji 显示

#### 允许的 Emoji 及使用场景
| Emoji | 含义 | 使用场景 |
|-------|------|----------|
| ⚠️ | 警告 | 重要注意事项、陷阱、已知问题 |
| 🔥 | 性能相关 | 性能敏感代码、热路径 |
| ⚡ | 优化 | 性能优化、算法改进 |
| 🔧 | 调试/工具 | 调试代码、临时方案 |

```python
# ✅ 推荐（注释中使用）
# ⚠️ 严重教训：曾因编码问题导致文档乱码
# 🔥 性能敏感：此函数在主循环中高频调用（20 Hz）
# ⚡ 优化：使用缓存避免重复计算

# ❌ 禁止（命令行输出中使用）
print("⚠️ 错误：参数超出范围")  # 终端可能不支持
LOG.info("🔥 性能警告：推理耗时过长")  # 日志输出不应有 Emoji
```

---

## 4. 代码结构

### 4.1 导入顺序
- **分组**：标准库 → 第三方库 → 本地模块
- **组间空行**：每组之间空一行
- **排序**：每组内按字母顺序排列

```python
# ✅ 推荐
# 标准库
import queue
import threading
import time

# 第三方库
import cv2
import numpy as np
import serial as s

# 本地模块
from bot import conn
import logger as LOG
```

### 4.2 全局变量管理
- **位置**：模块顶部集中定义（导入语句之后）
- **类型提示**：必须有类型提示
- **线程安全**：使用锁保护共享资源

```python
# ✅ 推荐
# 全局变量集中定义
serial_conn: s.Serial | None = None
serial_conn_lock: threading.Lock = threading.Lock()

_rx_buf: str = ""
_rx_queue: queue.Queue[str] = queue.Queue()
_cmd_queue: queue.Queue[str] = queue.Queue()
```

### 4.3 导出接口
- **使用 `__all__`**：明确导出的公共 API
- **私有函数**：不出现在 `__all__` 中

```python
# ✅ 推荐
__all__ = [
    "move_gimbal",
    "move_gimbal_absolute",
    "set_gimbal_recenter",
    "rotate_gimbal",
]

def move_gimbal(pitch: float, yaw: float, vpitch: int, vyaw: int):
    """公共 API"""
    ...

def _move_gimbal(pitch: float | None, yaw: float | None, vpitch: int, vyaw: int):
    """内部实现，不导出"""
    ...
```

---

## 5. 错误处理

### 5.1 参数验证（硬件控制必须）
- **时机**：函数入口处立即验证
- **异常类型**：`ValueError`
- **错误信息**：包含参数名、实际值、有效范围

```python
# ✅ 推荐
def set_chassis_speed_3d(x: float, y: float, z: float):
    """
    设置底盘三维速度。
    
    Args:
        x (float): x 轴速度，范围 [-3.5, 3.5] m/s
        y (float): y 轴速度，范围 [-3.5, 3.5] m/s
        z (float): z 轴角速度，范围 [-600, 600] °/s
    
    Raises:
        ValueError: 参数超出范围
    """
    if not -3.5 <= x <= 3.5:
        raise ValueError(f"x speed {x} out of range [-3.5, 3.5]")
    if not -3.5 <= y <= 3.5:
        raise ValueError(f"y speed {y} out of range [-3.5, 3.5]")
    if not -600 <= z <= 600:
        raise ValueError(f"z speed {z} out of range [-600, 600]")
    
    conn.write_serial(f"chassis speed x {x} y {y} z {z};")
```

### 5.2 异常捕获
- **外部调用**：必须捕获异常并记录日志
- **日志函数**：使用 `LOG.exception()` 自动附加堆栈

```python
# ✅ 推荐
try:
    result = model.run(...)
except Exception as e:
    LOG.error(f"YOLO inference failed: {e}")
    return None
```

### 5.3 资源清理
- **使用 `finally`**：确保资源释放
- **适用场景**：文件操作、线程管理、硬件控制

```python
# ✅ 推荐
try:
    self._running = True
    self._thread = threading.Thread(target=self._worker)
    self._thread.start()
except Exception as e:
    LOG.exception(f"Failed to start thread: {e}")
finally:
    self._running = False
```

---

## 6. 设计模式

### 6.1 单例模式
- **实现**：双重检查锁定
- **适用**：Logger、全局配置管理

```python
# ✅ 推荐
class Logger:
    _instance: Logger | None = None
    _instance_lock: threading.Lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

### 6.2 装饰器模式
- **适用**：函数增强、权重设置

```python
# ✅ 推荐
def weight_setting(weight: float):
    """权重设置装饰器"""
    def decorator(func):
        func.weight = weight
        return func
    return decorator

@weight_setting(0.45)
def distance_weight(target_info: tuple) -> float:
    ...
```

### 6.3 线程安全设计
- **共享资源**：必须用锁保护
- **命名**：锁变量名 `xxx_lock`

```python
# ✅ 推荐
serial_conn: s.Serial | None = None
serial_conn_lock: threading.Lock = threading.Lock()

def write_serial(data: str):
    with serial_conn_lock:
        if serial_conn:
            serial_conn.write(data.encode())
```

---

## 7. 特殊场景规范

### 7.1 硬件控制代码
- **类型提示**：100% 覆盖
- **参数验证**：必须验证范围
- **错误处理**：必须捕获异常
- **文档字符串**：必须包含参数范围说明

```python
# ✅ 推荐
def move_gimbal(pitch: float, yaw: float, vpitch: int, vyaw: int) -> None:
    """
    控制云台运动（相对角度）。
    
    Args:
        pitch (float): 俯仰轴相对角度，范围 [-55, 55]
        yaw (float): 偏航轴相对角度，范围 [-55, 55]
        vpitch (int): 俯仰轴速度，范围 [0, 540]
        vyaw (int): 偏航轴速度，范围 [0, 540]
    
    Raises:
        ValueError: 参数超出范围
    """
    if not -55 <= pitch <= 55:
        raise ValueError(f"pitch {pitch} out of range [-55, 55]")
    if not -55 <= yaw <= 55:
        raise ValueError(f"yaw {yaw} out of range [-55, 55]")
    if not 0 <= vpitch <= 540:
        raise ValueError(f"vpitch {vpitch} out of range [0, 540]")
    if not 0 <= vyaw <= 540:
        raise ValueError(f"vyaw {vyaw} out of range [0, 540]")
    
    _move_gimbal(pitch, yaw, vpitch, vyaw)
```

### 7.2 性能敏感代码
- **标记**：使用 🔥 Emoji 注释
- **原则**：避免阻塞操作、复杂计算
- **优化**：缓存、预计算、算法优化

```python
# ✅ 推荐
# 🔥 性能敏感：此函数在主循环中高频调用（20 Hz）
def select_target(targets: list[tuple]) -> int:
    if not targets:
        return -1
    
    # ⚡ 优化：使用缓存避免重复计算
    scores = [self._calculate_score(t) for t in targets]
    return max(range(len(scores)), key=lambda i: scores[i])
```

### 7.3 调试代码
- **标记**：使用 🔧 Emoji 或 TODO 注释
- **原则**：临时调试代码应在提交前移除或标记

```python
# ✅ 推荐
# 🔧 调试：观察目标选择过程
# TODO: 提交前移除
if config.DEBUG_MODE:
    LOG.debug(f"Selected target {target_id} with score {max_score}")
```

---

## 8. 反面示例

### 8.1 命名不当
```python
# ❌ 不推荐
def process(d):  # 函数名和参数名过于模糊
    ...

sc = None  # 变量名过于简短
chassisSpeed = 1.0  # 使用驼峰命名
_PublicFunction()  # 公共函数不应有下划线前缀
```

### 8.2 缺少类型提示
```python
# ❌ 不推荐（硬件控制代码）
def move_gimbal(pitch, yaw, vpitch, vyaw):  # 缺少类型提示
    ...

serial_conn = None  # 全局变量缺少类型提示
```

### 8.3 Emoji 误用
```python
# ❌ 禁止（命令行输出）
print("⚠️ 错误：参数超出范围")  # 终端可能不支持
LOG.info("🔥 性能警告")  # 日志输出不应有 Emoji

# ❌ 不推荐（滥用 Emoji）
# 🎉🎉🎉 成功启动 🎉🎉🎉  # 过度使用
# 💯 完美的代码 💯  # 无意义的 Emoji
```

### 8.4 注释不当
```python
# ❌ 不推荐
x = x + 1  # x 自增  # 无意义的注释（代码已经足够清晰）

# 设置速度
set_speed(1.0)  # 重复代码内容的注释

# TODO  # 缺少具体描述
```

---

## 9. 工具与环境

### 9.1 编码规范
- **文件编码**：UTF-8（无 BOM）
- **验证方法**：VS Code 右下角查看编码显示

### 9.2 代码检查
- **类型检查**：建议使用 `mypy`（可选）
- **格式检查**：建议使用 `black`（可选）

### 9.3 Git 提交前检查
参考 `copilot-instructions.md` 中的"提交前检查清单"

---

## 10. 总结

### 核心要点
1. **命名**：snake_case 函数/变量，PascalCase 类/类型，动词_名词格式
2. **类型提示**：Python 3.10+ 新语法，公共函数 100% 覆盖
3. **注释**：口语化可接受，Emoji 仅限注释/文档，禁止命令行输出
4. **文档字符串**：Google 风格，复杂函数必须有详细说明
5. **错误处理**：硬件控制必须验证参数范围

### AI 助手使用建议
- 生成代码前，先阅读本文档和 `copilot-instructions.md`
- 遇到不确定的风格问题，参考现有代码
- 生成代码后，检查是否符合本文档规范
- 特别关注硬件控制代码的类型提示和参数验证

---

**版本历史**：
- v1.0 (2025/10/05)：初始版本，基于项目现有代码分析
