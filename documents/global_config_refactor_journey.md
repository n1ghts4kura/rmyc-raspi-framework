# 全局配置文件重构记录

## 重构时间
2025年10月3日

## 重构目标
将 `aimassistant/config.py` 提升为全局配置文件 `src/config.py`，统一管理整个项目的配置参数。

## 重构动机
1. **避免配置分散**：原先配置散落在各个模块中（logger.py 的 DEBUG_MODE、conn.py 的串口参数、recognizer.py 的模型路径等）
2. **提升可维护性**：集中管理便于快速定位和修改参数
3. **增强一致性**：确保所有模块使用统一的配置来源
4. **简化部署**：修改运行环境参数时只需编辑一个文件

## 重构内容

### 1. 创建全局 `src/config.py`
包含以下配置分组：

#### 日志系统配置
```python
DEBUG_MODE = True  # 调试模式开关
```

#### 串口通信配置
```python
SERIAL_PORT = "/dev/ttyUSB0"   # Linux: /dev/ttyUSB0, Windows: COM3
SERIAL_BAUDRATE = 115200       # 波特率
SERIAL_TIMEOUT = 1             # 读取超时（秒）
```

#### 视觉识别配置
```python
YOLO_MODEL_PATH = "./model/yolov8n.onnx"  # 模型路径
CAMERA_WIDTH = 480
CAMERA_HEIGHT = 320
CAMERA_INDEX = 0
```

#### 自瞄系统配置
```python
CAMERA_FOV_HORIZONTAL = 70.0   # 水平视场角（度）
CAMERA_FOV_VERTICAL = 46.7     # 垂直视场角（度）
GIMBAL_SPEED = 90              # 云台运动速度（°/s）
MAX_YAW = 50                   # 最大偏航角限制（°）
MAX_PITCH = 50                 # 最大俯仰角限制（°）
AIM_LOST_TARGET_TIMEOUT_FRAMES = 12  # 连续无目标的帧数阈值
AIM_CONTROL_FREQUENCY = 20           # 自瞄控制频率（Hz）
```

### 2. 更新受影响的模块

#### `logger.py`
- **修改前**：本地定义 `DEBUG_MODE = True`
- **修改后**：`import config` 并使用 `config.DEBUG_MODE`
- **变更函数**：`set_debug_mode()` 中移除 `global DEBUG_MODE`，直接修改 `config.DEBUG_MODE`

#### `bot/conn.py`
- **修改前**：硬编码 `_device_address = "/dev/ttyUSB0"`, `baudrate=115200`, `timeout=10`
- **修改后**：使用 `config.SERIAL_PORT`, `config.SERIAL_BAUDRATE`, `config.SERIAL_TIMEOUT`

#### `recognizer.py`
- **修改前**：硬编码 `self.model_path = "./model/yolov8n.onnx"`
- **修改后**：使用 `config.YOLO_MODEL_PATH`

#### `aimassistant/angle.py`
- **修改前**：`from aimassistant.config import CAMERA_FOV_HORIZONTAL, CAMERA_FOV_VERTICAL`
- **修改后**：`import config` 并使用 `config.CAMERA_FOV_HORIZONTAL/VERTICAL`

#### `aimassistant/pipeline.py`
- **修改前**：`from aimassistant.config import GIMBAL_SPEED`
- **修改后**：`import config` 并使用 `config.GIMBAL_SPEED`

#### `skill/auto_aim_skill.py`
- **修改前**：本地定义 `LOST_TARGET_TIMEOUT_FRAMES = 12`, 硬编码 `time.sleep(0.05)`
- **修改后**：使用 `config.AIM_LOST_TARGET_TIMEOUT_FRAMES` 和 `time.sleep(1.0 / config.AIM_CONTROL_FREQUENCY)`

### 3. 删除旧文件
- ✅ 删除 `src/aimassistant/config.py`（功能已迁移到全局 config.py）

## 验证结果

### 编译测试
```powershell
✅ config.py 编译通过
✅ logger.py 无语法错误
✅ bot/conn.py 无语法错误
✅ recognizer.py 无语法错误
✅ aimassistant/angle.py 无语法错误
✅ aimassistant/pipeline.py 无语法错误
✅ skill/auto_aim_skill.py 无语法错误
✅ main.py 无语法错误
```

### 导入测试
```python
import config
print(config.SERIAL_PORT)        # /dev/ttyUSB0
print(config.SERIAL_BAUDRATE)    # 115200
print(config.YOLO_MODEL_PATH)    # ./model/yolov8n.onnx
```

## 设计决策

### 为何使用全局变量而非配置类？
1. **简洁性**：直接 `config.PARAM_NAME` 访问，无需实例化
2. **一致性**：与原项目风格保持一致（参考 `logger.py` 的 `DEBUG_MODE`）
3. **无状态**：配置参数为静态常量，不需要对象封装

### 为何不使用 YAML/JSON 配置文件？
1. **依赖最小化**：避免引入 PyYAML 等额外依赖
2. **类型安全**：Python 代码中的常量有 IDE 类型提示支持
3. **注释丰富**：直接在代码中添加 TODO 和说明
4. **开发便捷**：无需解析步骤，直接导入即用

### 为何不使用环境变量？
1. **复杂度低**：当前项目规模不需要环境变量隔离
2. **调试友好**：配置在代码中可见，便于 debug
3. **部署简单**：单机器人应用无需多环境切换

## 后续优化建议

### 短期（当前版本保持）
- ✅ 保持当前全局变量设计
- ⏳ 硬件测试后根据实际值更新 FOV、GIMBAL_SPEED 等参数

### 中期（v2.0 考虑）
- 添加配置验证函数（检查参数范围合法性）
- 支持从命令行参数覆盖配置（如 `--debug`, `--port COM3`）

### 长期（多机器人部署时）
- 考虑引入 YAML 配置文件（`config.yaml`）
- 实现配置热重载机制
- 添加配置版本管理

## 文件结构变化

```diff
src/
├── config.py                      [新增] 全局配置文件
├── logger.py                      [修改] 使用 config.DEBUG_MODE
├── recognizer.py                  [修改] 使用 config.YOLO_MODEL_PATH
├── bot/
│   └── conn.py                    [修改] 使用 config.SERIAL_*
├── aimassistant/
│   ├── config.py                  [删除] 功能迁移到全局 config
│   ├── angle.py                   [修改] 使用 config.CAMERA_FOV_*
│   └── pipeline.py                [修改] 使用 config.GIMBAL_SPEED
└── skill/
    └── auto_aim_skill.py          [修改] 使用 config.AIM_*
```

## 注意事项
1. **串口路径**：Linux 使用 `/dev/ttyUSB0`，Windows 需改为 `COM3` 等
2. **FOV 校准**：`CAMERA_FOV_HORIZONTAL/VERTICAL` 为估算值，需硬件测试校准
3. **控制频率**：`AIM_CONTROL_FREQUENCY = 20Hz` 需根据视觉识别实际 FPS 调整
4. **导入顺序**：确保 `import config` 在其他模块导入之前（避免循环导入）

## 测试清单
- [x] 所有 Python 文件编译通过
- [x] config.py 语法正确
- [x] 导入测试通过（config 模块可正常加载）
- [ ] 主程序运行测试（需 Raspberry Pi 环境）
- [ ] 串口通信测试（验证 SERIAL_* 参数）
- [ ] 视觉识别测试（验证 YOLO_MODEL_PATH）
- [ ] 自瞄功能测试（验证 FOV、GIMBAL_SPEED 等参数）
