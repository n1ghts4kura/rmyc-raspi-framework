---
title:  代码风格与约定总览
status: draft
version: v1.1-re
category: reference
---

> 说明：本文件是对本项目现有编码约定的汇总，
> 目标是给人类开发者和 LLM 一个「最低限度但足够用」的统一参考。
> 更详细/动态的约定，请以 `docs/principles.md` 与 `.github/copilot-instructions.md` 为准。

## 1. 命名风格

- 函数：`verb_noun`，例如：`set_chassis_speed`、`move_gimbal`。
- 变量：`lowercase_underscore`，例如：`serial_conn`、`frame_buffer`。
- 私有成员：前缀单下划线，例如：`_rx_buf`、`_stop_event`。
- 常量：`UPPERCASE_UNDERSCORE`，例如：`SERIAL_TIMEOUT`、`CAMERA_WIDTH`。

## 2. 类型注解（Type Hints）

- 所有「对外公开」的函数/方法必须带有类型注解。
- 推荐导入：`from typing import Optional, List, Tuple, Dict`。
- 返回 `None` 时显式写出，避免省略。

```python
from typing import Optional

def move_gimbal(pitch: float, yaw: float, speed: int = 90) -> None:
    """控制云台转动。"""
    ...
```

## 3. 文件编码与路径约定

- 所有源代码与文档文件一律使用 **UTF-8（无 BOM）**。
- 路径约定：
  - 开发机是 Windows，但运行环境是树莓派 Linux；
  - 代码和文档中的路径统一使用 `/`；
  - 串口设备路径示例：`/dev/ttyUSB0`，避免写成 `COM3`。

## 4. 硬件控制代码的参数校验

- 所有直接下发到底盘/云台/发射器的控制函数，必须做参数范围检查。
- 建议在 docstring 中写清范围，并在运行时使用 `if not ...: raise ValueError(...)`。

```python
def set_chassis_speed_3d(x: float, y: float, z: float) -> None:
    """设置底盘三维速度。

    Args:
        x: 前进方向速度，单位 m/s，范围 [-3.5, 3.5]
        y: 横向速度，单位 m/s，范围 [-3.5, 3.5]
        z: 旋转速度，单位 °/s，范围 [-600, 600]
    """
    if not -3.5 <= x <= 3.5:
        raise ValueError(f"x speed {x} out of range [-3.5, 3.5]")
    # 其他轴类似处理
```

## 5. 日志与异常处理

- 外部依赖（串口、模型推理、文件 IO 等）必须使用 `try/except` 捕获异常，记录日志后再决定是否继续。
- 不要在底层库中直接 `print`，统一使用项目内的日志工具（例如 `logger.py` 中的封装）。

## 6. 与现有文档的关系

- 本文是对 `.github/copilot-instructions.md` 与 `docs/principles.md` 中「编码相关部分」的精简汇总：
  - 若两者与本文存在不一致，以 `.github/copilot-instructions.md` 与 `docs/principles.md` 为准；
  - 后续如有新的强制编码规范，应优先更新上述两处，再视情况同步本文件。
