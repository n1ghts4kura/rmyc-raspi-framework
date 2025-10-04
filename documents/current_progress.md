# 项目开发进展分析

**分析日期**: 2025年10月4日  
**最后更新**: 2025年10月4日（文档归档整理）  
**分析者**: GitHub Copilot  
**目的**: 完整阅读整个项目，分析当前开发状态和已完成功能

---

## 📊 项目概况

### 项目定位
- **名称**: RMYC Raspi Framework
- **用途**: 使用 Raspberry Pi 控制 DJI RoboMaster S1/EP 机器人
- **目标赛事**: 机甲大师空地协同对抗赛（RMYC）
- **开发语言**: Python 3.11+
- **硬件平台**: Raspberry Pi 4B 4GB
- **当前分支**: dev_v1_1

### 技术栈
- **核心框架**: Python 3.11
- **视觉识别**: YOLOv8n (ONNX Runtime)
- **通信协议**: UART (串口，115200 波特率)
- **调试工具**: Prompt Toolkit (异步 REPL)
- **AI/ML**: Ultralytics, ONNX Runtime, OpenCV

---

## 🗂️ 代码结构分析

### 源码目录结构
```
src/
├── config.py                  # ✅ 全局配置系统（新增）
├── context.py                 # 全局上下文
├── logger.py                  # 彩色日志系统
├── main.py                    # 主程序入口
├── recognizer.py              # 视觉识别器（双线程）
├── repl.py                    # 串口调试 REPL
├── bot/                       # 硬件抽象层
│   ├── conn.py                # 串口通信
│   ├── sdk.py                 # SDK 模式切换
│   ├── chassis.py             # 底盘控制
│   ├── gimbal.py              # ✅ 云台控制（支持360°旋转）
│   ├── blaster.py             # 发射器控制
│   ├── game_msg.py            # 赛事消息解析
│   └── robot.py               # 机器人状态查询
├── skill/                     # 技能系统
│   ├── base_skill.py          # 技能基类
│   ├── manager.py             # 技能管理器
│   ├── example_skill.py       # 示例技能
│   └── auto_aim_skill.py      # ✅ 自瞄技能（新增）
└── aimassistant/              # ✅ 自瞄系统（新增模块）
    ├── selector.py            # 目标选择器
    ├── angle.py               # 角度解算
    └── pipeline.py            # 自瞄主管线
```

### 工具脚本
```
tools/
├── convert_pt_to_onnx.py               # 模型转换工具
├── set_cpu_performance.sh              # CPU 性能模式（临时）
├── install_cpu_performance_service.sh  # 安装性能服务
├── uninstall_cpu_performance_service.sh
└── verify_power.sh                     # 电源诊断
```

---

## ✅ 已完成功能模块

### 1. 基础框架层（v1.0 核心）

#### 串口通信系统 (`bot/conn.py`)
- ✅ 串口打开/关闭
- ✅ 后台接收线程（双队列：行级、命令级）
- ✅ 非阻塞读取（`get_serial_command_nowait()`）
- ✅ 线程安全锁保护
- ✅ 自动权限设置（Linux chmod 777）
- **状态**: 稳定，生产可用

#### SDK 模式控制 (`bot/sdk.py`)
- ✅ `enter_sdk_mode()` - 进入 SDK 模式
- ✅ `exit_sdk_mode()` - 退出 SDK 模式
- **状态**: 完成

#### 硬件控制 API (`bot/`)
- ✅ **底盘控制** (`chassis.py`)
  - 速度控制（3D 运动）
  - 轮速控制
  - 相对位置控制
  - 姿态查询
- ✅ **云台控制** (`gimbal.py`)
  - ✅ 基础控制（±55° 限制）
  - ✅ **360° 无限旋转**（`rotate_gimbal`, 滑环支持）
  - ✅ 角度分解算法（大角度 → 多步进）
  - ✅ 时间计算公式（物理模型）
  - 回中功能
  - 姿态查询
- ✅ **发射器控制** (`blaster.py`)
  - 水弹发射
  - LED 灯控制
- ✅ **赛事消息解析** (`game_msg.py`)
  - 键鼠数据解析
  - 结构化字典输出
- **状态**: 完成，已验证

#### 技能系统 (`skill/`)
- ✅ **技能基类** (`base_skill.py`)
  - 线程化执行
  - 状态管理（enabled）
  - 键位绑定
- ✅ **技能管理器** (`manager.py`)
  - 技能注册
  - 按键触发
  - 互斥取消
  - 状态查询
- ✅ **示例技能** (`example_skill.py`)
  - 按键 'w' 绑定
  - 演示技能生命周期
- **状态**: 完成，架构稳定

#### 日志系统 (`logger.py`)
- ✅ 彩色控制台输出
- ✅ 级别分类（DEBUG/INFO/WARNING/ERROR）
- ✅ 调试模式开关（`DEBUG_MODE`）
- ✅ 异常堆栈自动记录
- **状态**: 完成

#### REPL 调试工具 (`repl.py`)
- ✅ 异步串口交互
- ✅ 彩色输出（发送/接收/警告）
- ✅ 时间戳显示
- ✅ 内置命令（:q, :help, :eol）
- ✅ SSH 环境支持
- **状态**: 完成，文档完善 (`documents/repl.md`)

---

### 2. 视觉识别系统

#### Recognizer 模块 (`recognizer.py`)
- ✅ **双线程架构**
  - 采集线程（摄像头读取）
  - 推理线程（YOLO 检测）
- ✅ **单例模式**（技能模块直接获取实例）
- ✅ **性能优化**
  - 完全非阻塞推理循环
  - CPU 核心绑定
  - 智能跳帧策略
- ✅ **性能指标**（经优化）
  - 推理 FPS: **4.15** (稳定)
  - 推理时间: ~240ms
  - 标准差: ±6.5ms（极其稳定）
  - 系统效率: 96%（接近硬件极限）
- ✅ **模型支持**
  - YOLOv8n ONNX（480×320 输入）
  - ONNX Runtime CPU 后端
- ✅ **可视化支持**
  - `imshow()` 调试显示
  - 标注框绘制
  - FPS 信息叠加
- **状态**: 已完成性能优化（0.72 FPS → 4.15 FPS），生产就绪
- **优化记录**: `documents/PERFORMANCE_OPTIMIZATION_JOURNEY.md`

---

### 3. 自瞄系统（v1.0）✨ 新增

#### 目标选择器 (`aimassistant/selector.py`)
- ✅ **权重装饰器系统**
  - `@weight_setting(weight)` 装饰器
  - 自动收集评分因子
- ✅ **三个评分因子**
  - `box_square_factor_v1` - 面积因子（权重 0.5）
  - `box_center_factor_v1` - 中心距离因子（权重 0.3）
  - `confidence_factor_v1` - 置信度因子（权重 0.2）
- ✅ **选择器实现** (`selector_v1`)
  - 综合评分排序
  - 返回最优目标
- **状态**: 完成

#### 角度解算 (`aimassistant/angle.py`)
- ✅ **针孔相机模型**
  - 基于归一化坐标 → 角度转换
  - 自动计算垂直 FOV（从水平 FOV 推导）
- ✅ **公式实现**
  ```python
  yaw = (xn - 0.5) × FOV_horizontal
  pitch = -(yn - 0.5) × FOV_vertical_calculated
  ```
- ✅ **FOV 配置改进**
  - 只配置水平 FOV（符合工程实践）
  - 垂直 FOV 自动计算（避免冗余参数）
- **状态**: 完成，符合数学模型

#### 自瞄主管线 (`aimassistant/pipeline.py`)
- ✅ **核心流程函数** (`aim_step_v1`)
  - 检测 → 选择 → 解算 → 控制
  - 非阻塞设计
  - 返回是否成功瞄准
- ✅ **云台回中** (`recenter_gimbal`)
  - 目标丢失时恢复初始位置
- **状态**: 完成，过程式设计

#### 自瞄技能集成 (`skill/auto_aim_skill.py`)
- ✅ **技能绑定**: 'z' 键
- ✅ **目标丢失处理**
  - 连续 12 帧（~3s）无目标后自动回中
  - 丢失计数器管理
- ✅ **控制频率**: 20 Hz（可配置）
- ✅ **与技能系统无缝集成**
- **状态**: 完成，等待硬件测试

#### 主程序集成 (`main.py`)
- ✅ 注册 `auto_aim_skill` 到技能管理器
- ✅ 为自瞄技能传递 `recognizer` 参数
- ✅ 按键 'z' 触发自瞄开关
- **状态**: 完成

---

### 4. 全局配置系统 ✨ 新增

#### 配置文件 (`config.py`)
- ✅ **统一配置管理**
  - 日志系统配置
  - 串口通信配置
  - 视觉识别配置
  - 自瞄系统配置
- ✅ **设计特点**
  - 全局变量方式（简洁、类型安全）
  - 无需 YAML/JSON（减少依赖）
  - 直接导入访问（`import config`）
- ✅ **配置项**（关键参数）
  ```python
  # 串口
  SERIAL_PORT = "/dev/ttyUSB0"
  SERIAL_BAUDRATE = 115200
  
  # 视觉
  YOLO_MODEL_PATH = "./model/yolov8n.onnx"
  CAMERA_WIDTH = 480
  CAMERA_HEIGHT = 320
  
  # 自瞄
  CAMERA_FOV_HORIZONTAL = 70.0  # TODO: 校准
  GIMBAL_SPEED = 90             # TODO: 调优
  AIM_LOST_TARGET_TIMEOUT_FRAMES = 12
  AIM_CONTROL_FREQUENCY = 20
  ```
- **状态**: 完成，已迁移所有分散配置
- **重构记录**: `documents/global_config_refactor_journey.md`

---

### 5. 硬件改装支持 ✨ 新增

#### 滑环云台 360° 旋转 (`bot/gimbal.py`)
- ✅ **角度分解算法**
  - 大角度 → 多个 ≤50° 步进
  - 自动计算等待时间（基于物理公式）
  - 公式: `t = |angle| / speed + 0.1s`
- ✅ **主操作函数**
  - `rotate_gimbal()` - 相对角度 360° 旋转
  - `rotate_gimbal_absolute()` - 绝对角度 360° 旋转
- ✅ **向后兼容**
  - 保留 `_move_gimbal()` 作为内部函数
  - 旧代码仍可工作（±55° 限制）
- ✅ **自瞄集成**
  - `pipeline.py` 已使用 `rotate_gimbal()`
  - 突破 ±55° 限制
- **状态**: 代码完成，待硬件测试（缓冲时间调优）
- **实现记录**: `documents/gimbal_360_implementation_journey.md`

---

## 📈 性能优化成果

### 优化历程（2025年10月2日）
- **阶段 1**: 主循环优化
  - 问题: `time.sleep(0.001)` 实际睡眠 37ms
  - 解决: 移除 sleep，完全非阻塞
  - 成果: 3.82 FPS → 10,192 FPS（2,667x）

- **阶段 2**: CPU 降频问题
  - 问题: 劣质电源导致 CPU 降频至 700 MHz
  - 解决: 更换 5V 3A 电源，设置性能模式
  - 成果: 推理时间 611ms → 231ms（2.65x）

- **阶段 3**: 后端选择
  - 问题: NCNN Vulkan 不稳定（频繁崩溃）
  - 解决: 改用 ONNX Runtime CPU 后端
  - 成果: 稳定性提升 23x（标准差 ±153ms → ±6.5ms）

- **阶段 4**: 推理线程阻塞
  - 问题: 主循环饥饿（47k FPS 疯狂轮询）
  - 解决: 智能休眠策略（推理未更新时休眠）
  - 成果: 系统集成 0.72 FPS → 4.15 FPS（5.76x）

### 最终性能指标
- ✅ **推理 FPS**: 4.15（稳定）
- ✅ **推理时间**: ~240ms（平均）
- ✅ **稳定性**: 4.06-4.17 FPS（波动 ±0.05）
- ✅ **系统效率**: 96%（接近硬件极限）
- ✅ **达标情况**: 满足实时控制需求（≥4 FPS，<250ms 延迟）

### 工具脚本产出
- ✅ `tools/verify_power.sh` - 电源诊断
- ✅ `tools/set_cpu_performance.sh` - 性能模式切换
- ✅ `tools/install_cpu_performance_service.sh` - 开机自启服务

**详细记录**: 
- `documents/PERFORMANCE_OPTIMIZATION_JOURNEY.md` (完整过程)
- `documents/PERFORMANCE_OPTIMIZATION_SUMMARY.md` (成果总结)

---

## 🧹 项目清理（2025年10月3日）

### 清理成果
- ✅ 删除测试脚本（3 个）
  - `test_inference_loop.py`
  - `test_low_power.py`
  - `test_onnx_performance.py`
- ✅ 删除工具脚本（6 个）
  - NCNN 相关工具（已弃用）
  - 过时的相机测试脚本
- ✅ 重构演示工具
  - `test_annotation.py` → `demo_vision.py`
  - 简化代码（167 行 → 120 行）
- ✅ 总计减少代码: ~1647 行

**清理记录**: `documents/project_cleanup_journey.md`

---

## 📚 文档系统

### 核心文档（当前 14 个）
1. **技术参考**
   - `sdk_protocol_api_document.md` - RoboMaster SDK 协议手册

2. **工具说明**
   - `repl.md` - REPL 调试工具使用指南

3. **架构总览**
   - `general_intro_for_ai.md` - 项目架构（面向 AI 协作）

4. **模块设计**
   - `aimassistant_intro_for_ai.md` - 自瞄系统设计方案

5. **开发过程记录** (journey 文档，9 个)
   - `aimassistant_implementation_journey.md`
   - `recognizer_simplification_journey.md`
   - `PERFORMANCE_OPTIMIZATION_JOURNEY.md`
   - `project_cleanup_journey.md`
   - `uart_feedback_decision_journey.md`
   - `gimbal_360_implementation_journey.md`
   - `global_config_refactor_journey.md`
   - `fov_config_improvement_journey.md`

6. **里程碑总结** (2 个)
   - `aimassistant_v1_completion.md` - 自瞄 v1.0 完成标记
   - `PERFORMANCE_OPTIMIZATION_SUMMARY.md` - 性能优化总结

### 文档状态分析
- ✅ **当前有效**: 11 个文档
- ⚠️ **部分过时**: 3 个文档（需更新）
  - `general_intro_for_ai.md` - 未包含全局配置、自瞄 v1.0
  - `aimassistant_intro_for_ai.md` - 设计方案 vs 实际简化实现
  - `aimassistant_implementation_journey.md` - 部分内容被后续 journey 覆盖

---

## 🔮 待完成功能与技术债务

### 1. 硬件测试与参数校准
- ⏳ **自瞄系统实机测试**
  - FOV 参数校准（当前 70° 为估算值）
  - 云台速度调优（当前 90°/s）
  - 目标丢失阈值调整（当前 12 帧）
  - 控制频率验证（当前 20 Hz）

- ⏳ **360° 旋转功能验证**
  - 滑环硬件测试
  - 时间缓冲参数调优（当前 0.1s）
  - 大角度旋转稳定性测试

### 2. 串口反馈机制
- ⏳ **待验证问题**（需硬件测试）
  - 控制指令是否返回 `ok;`
  - 非阻塞发送的指令丢失率
  - 云台/底盘控制精度
  - 指令执行延迟实际值

- 💡 **预留扩展方案**（按需实现）
  - 方案 A: 阻塞版本 API（`move_gimbal_wait()`）
  - 方案 B: 统一反馈验证层（`write_serial_and_wait()`）
  - 方案 C: 基于状态查询的验证

**决策记录**: `documents/uart_feedback_decision_journey.md`

### 3. 自瞄系统扩展（未实现）
- 💡 **单目测距模块** (`distance.py`)
  - 为卡尔曼滤波提供距离信息
  - 基于相似三角形原理

- 💡 **卡尔曼滤波预测** (`kalman.py`)
  - 预测移动目标位置
  - 提供提前量计算

- 💡 **自适应性能管理** (`adaptive.py`)
  - 三种模式：fast / balanced / precise
  - 动态调整精度与速度平衡

**设计存档**: `documents/aimassistant_intro_for_ai.md`（完整设计方案）

### 4. 文档更新
- ⏳ **高优先级**: 更新 `general_intro_for_ai.md`
  - 补充全局配置系统章节
  - 更新自瞄模块实现状态
  - 添加性能优化成果
  - 更新技术栈（ONNX Runtime）

- ⏳ **中优先级**: 标注 `aimassistant_intro_for_ai.md`
  - 添加"实际实现状态"章节
  - 区分已实现 vs 未实现功能
  - 或重命名为 `aimassistant_design_archive.md`

---

## 🎯 当前开发状态总结

### 项目版本
- **当前分支**: dev_v1_1
- **当前状态**: 自瞄系统 v1.0 开发完成，等待硬件测试

### 核心成就
1. ✅ **基础框架完善**（v1.0）
   - 串口通信系统稳定
   - 技能系统架构完整
   - 硬件控制 API 齐全
   - REPL 调试工具强大

2. ✅ **性能优化突破**（v1.0）
   - 推理 FPS 从 0.72 → 4.15（5.76x）
   - 系统效率达到 96%（接近硬件极限）
   - 稳定性极高（±6.5ms 标准差）

3. ✅ **自瞄系统实现**（v1.1 新增）
   - 目标选择器完成（权重评分系统）
   - 角度解算完成（针孔相机模型）
   - 自瞄主管线完成（过程式设计）
   - 技能系统集成完成（'z' 键触发）

4. ✅ **全局配置系统**（v1.1 新增）
   - 统一配置管理
   - 减少配置分散
   - 简化部署流程

5. ✅ **360° 旋转支持**（v1.1 新增）
   - 角度分解算法
   - 时间计算公式
   - 突破硬件限制

### 待测试项
- ⏳ 自瞄系统实机验证（树莓派 + 机器人）
- ⏳ FOV 参数校准
- ⏳ 云台速度调优
- ⏳ 360° 旋转硬件测试

### 下一步建议
1. **立即**: 在树莓派上运行 `python src/main.py`，测试自瞄功能
2. **校准**: 根据实际效果调整 `config.py` 中的参数
3. **反馈**: 记录测试结果，迭代优化
4. **文档**: 更新 `general_intro_for_ai.md` 补充最新进展

---

## 📊 代码统计

### 核心模块代码量（估算）
```
src/
├── main.py                    ~100 行
├── config.py                  ~60 行（新增）
├── logger.py                  ~80 行
├── recognizer.py              ~520 行（已优化）
├── repl.py                    ~200 行
├── bot/                       ~800 行
│   ├── conn.py                ~200 行
│   ├── gimbal.py              ~380 行（含360°旋转）
│   ├── chassis.py             ~150 行
│   └── 其他                   ~70 行
├── skill/                     ~250 行
│   ├── base_skill.py          ~80 行
│   ├── manager.py             ~100 行
│   └── auto_aim_skill.py      ~70 行（新增）
└── aimassistant/              ~200 行（新增）
    ├── selector.py            ~95 行
    ├── angle.py               ~48 行
    └── pipeline.py            ~76 行

总计: ~2,200 行（核心代码，不含测试）
```

### 文档代码量
```
documents/                     ~7,000 行
tools/                         ~300 行
README.md                      ~100 行
```

---

## 🔍 技术亮点

### 1. 双线程视觉识别架构
- **设计**: 采集线程 + 推理线程完全解耦
- **优势**: 避免推理阻塞采集，充分利用 CPU
- **成果**: 4.15 FPS 稳定性（96% 系统效率）

### 2. 全局配置系统
- **设计**: 全局变量 + 直接导入（无需实例化）
- **优势**: 简洁、类型安全、无额外依赖
- **统一**: 7 个模块迁移到统一配置

### 3. 滑环 360° 旋转算法
- **设计**: 角度分解 + 物理时间计算
- **创新**: 突破 UART ±55° 限制
- **公式**: `t = |angle| / speed + 0.1s`

### 4. 技能系统架构
- **设计**: 线程化 + 状态管理 + 键位绑定
- **扩展性**: 新增技能只需实现 `invoke_func`
- **灵活性**: 支持任意参数传递（kwargs）

### 5. REPL 调试工具
- **特色**: 异步 + 彩色输出 + SSH 支持
- **价值**: 独立调试环境，实时查看串口交互

---

## 🎓 经验教训记录

### 性能优化教训
1. ⚠️ **time.sleep() 陷阱**: Linux 下 `sleep(0.001)` 实际睡眠 37ms
2. ⚠️ **电源质量**: 劣质电源导致 62% 性能损失
3. ⚠️ **NCNN Vulkan**: 树莓派上极度不稳定
4. ⚠️ **CPU 资源竞争**: 主循环疯狂轮询会饿死推理线程

### 工程实践教训
1. ✅ **FOV 配置**: 只配置水平 FOV，垂直 FOV 自动计算
2. ✅ **配置集中**: 避免分散配置，统一管理
3. ✅ **文档先行**: journey 文档记录决策过程
4. ✅ **过程式设计**: 自瞄系统采用纯函数，避免过度封装

---

## 📅 版本演进时间线（推测）

### v1.0 阶段（基础框架）
**时间**: 2025年9月~10月初  
**关键成就**:
- ✅ 串口通信系统
- ✅ 技能系统架构
- ✅ 硬件控制 API
- ✅ 视觉识别器
- ✅ REPL 调试工具
- ✅ 性能优化（0.72 → 4.15 FPS）

### v1.1 阶段（自瞄系统）
**时间**: 2025年10月3日~10月4日  
**关键成就**:
- ✅ 自瞄系统实现（selector + angle + pipeline + skill）
- ✅ 全局配置系统
- ✅ 滑环 360° 旋转
- ✅ FOV 配置改进
- ✅ 项目清理

**当前状态**: 代码开发完成，等待硬件测试

---

## � 文档归档整理（2025年10月4日）

### 归档操作
为保持核心文档的简洁性和可维护性，将已完成功能的详细实现过程文档移至 `documents/archive/` 目录。

### 归档文档（4个，~1,541 行）
1. **aimassistant_implementation_journey.md** (417行) - 自瞄系统实现细节
2. **gimbal_360_implementation_journey.md** (252行) - 云台360°旋转实现
3. **recognizer_simplification_journey.md** (419行) - 视觉识别优化过程
4. **PERFORMANCE_OPTIMIZATION_JOURNEY.md** (453行) - 性能优化详细过程

### 保留文档（9个，~3,315 行）
1. **general_intro_for_ai.md** (81行) - 架构总览
2. **aimassistant_intro_for_ai.md** (149行) - 自瞄系统设计
3. **current_progress.md** (499行) - 项目进展分析
4. **development_history_v1.md** (535行) - v1.0 开发历程
5. **development_history_v1_1.md** (805行) - v1.1 开发历程
6. **sdk_protocol_api_document.md** (409行) - SDK 协议手册
7. **repl.md** (64行) - REPL 工具说明
8. **PERFORMANCE_OPTIMIZATION_SUMMARY.md** (166行) - 性能优化总结
9. **uart_feedback_decision_journey.md** (607行) - 串口反馈机制设计决策（待硬件测试验证）

### 归档效果
- 核心文档数量：12个 → 9个（减少 25%）
- 核心文档行数：4,856行 → 3,315行（减少 32%）
- 文档/代码比：1.96:1 → 1.34:1（优化到理想范围）

归档文档仍保留在 Git 仓库中，可随时在 `documents/archive/` 目录查阅。

---

## �🚀 结论

**项目当前处于 v1.1 开发阶段末期**，自瞄系统核心功能已实现，等待硬件测试和参数调优。

**核心优势**:
- ✅ 架构清晰（三层设计）
- ✅ 性能优秀（4.15 FPS 稳定）
- ✅ 文档完善（14 个文档，~7000 行）
- ✅ 可扩展性强（技能系统、配置系统）

**下一步工作**:
1. 硬件测试（自瞄 + 360° 旋转）
2. 参数校准（FOV、云台速度）
3. 文档更新（general_intro_for_ai.md）
4. 迭代优化（根据测试结果）

---

**分析完成时间**: 2025年10月4日  
**分析者**: GitHub Copilot  
**置信度**: 高（基于完整代码和文档阅读）
