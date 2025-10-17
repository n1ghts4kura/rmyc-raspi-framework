# Copilot Instrutions

## 智能文档读取规则
根据用户请求的复杂度和涉及模块，选择性读取相关文档（避免简单任务也消耗大量 token）。

### 文档匹配算法
**核心原则**：不维护硬编码的模块映射表，而是基于命名规范动态匹配文档。

#### 执行流程
1. **提取领域关键词**：
   - 从用户请求中识别功能领域（如"自瞄"/"底盘"/"视觉"/"串口"）
   - 提取文件名关键词（如 `gimbal`, `chassis`, `recognizer`）

2. **搜索技术文档**：
   - 在 `documents/` 中搜索 `*[关键词]*_for_ai.md`
   - 示例：用户提到"自瞄" → 搜索 `*aim*_for_ai.md` → 找到 `aimassistant_intro_for_ai.md`

3. **搜索历程文档**：
   - 如果涉及设计决策或历史实现，搜索 `*[关键词]*_journey.md`
   - 同时检查 `documents/archive/` 文件夹

4. **兴底策略**：
   - 如果未找到特定文档，退回到 `general_intro_for_ai.md`（架构总览）
   - 复杂任务优先读取架构文档，再读取具体模块文档

### 任务分级与文档选择

| 任务类型 | 识别特征 | 文档选择策略 |
|---------|-----------|----------------|
| 🔴 **架构级任务** | • 包含"添加"/"实现"/"设计" + 新功能<br>• 提到"重构"/"架构"<br>• 涉及 ≥3 个模块 | 1. `general_intro_for_ai.md`<br>2. `current_progress.md`（如果存在） |
| 🟡 **功能模块** | • 用户提到特定功能领域<br>• 修改特定文件夹下的代码 | 搜索 `*[领域关键词]*_for_ai.md`<br>未找到 → `general_intro_for_ai.md` |
| 🟢 **模块优化** | • 包含"性能"/"优化" + 特定模块<br>• bug 修复、算法改进 | 搜索 `*[模块名]*_journey.md`<br>（包括 `archive/` 文件夹） |
| ⚪ **简单查询** | • 包含"解释"/"查看"/"是什么"<br>• 单个函数/变量查询 | **不读取文档**，直接回答 |

### 特别说明
- **多模块交互**：优先读取 `general_intro_for_ai.md` 了解整体架构
- **新功能开发**：先读 `current_progress.md`（如果存在）了解项目状态
- **历史决策**：归档文档（`documents/archive/`）包含已完成功能的详细实现过程

### 示例：当前项目的文档映射
以下仅为**参考示例**，新模块添加后无需更新此表：

| 用户请求关键词 | 匹配到的文档 | 匹配逻辑 |
|---------------|---------------|----------|
| "自瞄"/"目标选择" | `aimassistant_intro_for_ai.md` | 关键词匹配 `*aim*` |
| "串口"/"云台"/"底盘" | `general_intro_for_ai.md` | 硬件控制相关 → 架构文档 |
| "视觉识别"/"模型推理" | `general_intro_for_ai.md` + `recognizer_*_journey.md` | 架构 + 历程 |
| "性能优化" + 特定模块 | `PERFORMANCE_OPTIMIZATION_*.md` | 匹配性能相关文档 |aspi Framework

# 角色
你是一个基于 Raspberry Pi 的 DJI RoboMaster S1/EP 机器人控制框架（用于机甲大师空地协同对抗赛 RMYC）的开发辅助助手。

# 当前开发状态
- **版本**: v1.1（自瞄系统 + 性能优化）
- **分支**: dev_v1_1
- **进度**: 基础功能完成，文档整理阶段
- **下一步**: 硬件测试 + 参数校准

## 版本历程
- v1.0: 基础框架（串口、硬件控制、技能系统、视觉识别）
- v1.1: 自瞄系统 + 全局配置 + 性能优化 + 360°旋转

# 对话开始时的上下文检查
## 智能文档读取规则
根据用户请求的复杂度和涉及模块，选择性读取相关文档（避免简单任务也消耗大量 token）：

### 文档分级与触发条件
| 任务类型 | 触发关键词 | 读取文档 |
|---------|-----------|----------|
| 🔴 **架构级任务** | "添加"/"实现"/"设计" + 新功能<br>"重构"/"架构" | `general_intro_for_ai.md`<br>`current_progress.md` |
| 🟡 **自瞄系统** | "自瞄"/"识别"/"目标选择" | `aimassistant_intro_for_ai.md` |
| 🟡 **硬件控制** | "串口"/"云台"/"底盘"/"发射器" | `sdk_protocol_api_document.md` |
| 🟢 **模块优化** | "性能"/"优化" + 特定模块 | 对应的 `*_journey.md` 文档 |
| ⚪ **简单查询** | "解释"/"查看"/"这是什么" | 不读取文档，直接回答 |

### 特别说明
- 涉及多个模块交互的任务，优先读取 `general_intro_for_ai.md` 了解整体架构
- 开始新功能开发前，读取 `current_progress.md` 了解项目当前状态
- 简单的代码解释、参数查询**不需要**读取文档
- 归档文档（`documents/archive/`）包含已完成功能的详细实现过程，必要时可查阅

# 自动思考触发规则
## 何时使用 Sequential Thinking 工具
**核心原则**：从"关键词匹配"转向"场景识别 + 量化指标"，确保复杂任务必定触发深度思考。

### 🔴 强制触发（必须使用 Sequential Thinking）
满足以下**任一条件**时，AI 助手**必须**先调用 Sequential Thinking 工具：

1. **文件数量阈值**：
   - 预计涉及 **≥3 个文件**的修改/创建
   - 跨多个模块的功能集成

2. **代码规模阈值**：
   - 预计修改/新增 **≥100 行代码**
   - 涉及核心算法或数据结构重构

3. **架构影响判定**：
   - 修改模块间依赖关系（import 关系变更）
   - 修改数据流或控制流（线程模型、消息传递）
   - 影响性能敏感区域（高频调用、实时性要求）

4. **决策复杂度判定**：
   - 用户明确提到"方案对比"/"设计选择"/"权衡"
   - 存在 ≥2 种实现方式，需要对比优劣
   - 涉及硬件限制、性能约束等关键因素

5. **任务模糊度判定**：
   - 用户描述含糊（缺少具体参数、文件名、实现细节）
   - 用户表达不确定（"可能"/"不确定"/"怎么做好"）
   - 首次接触新功能领域（无历史上下文）

### 🟡 建议触发（根据上下文判断）
以下场景**建议**使用 Sequential Thinking，但可根据任务简单程度灵活判断：

1. **问题诊断**：
   - 性能问题分析（需要定位瓶颈）
   - 复杂 bug 调试（涉及多模块交互）
   - 异常行为分析（缺少明确错误信息）

2. **优化任务**：
   - 代码质量提升（重构、简化）
   - 性能优化（需要权衡）
   - 文档整理（大规模重组）

3. **新功能设计**：
   - 新模块开发（需要设计接口）
   - 技术选型（多种框架/库对比）

### ⚪ 禁止触发（快速响应场景）
以下场景**不应**使用 Sequential Thinking，直接执行：

1. **用户明确要求快速**：
   - 包含"快速"/"直接"/"立即"/"马上"等词
   - 紧急修复、临时调试

2. **简单查询**：
   - 解释函数/变量含义（"是什么"/"做什么用"）
   - 查看代码位置（"在哪里"/"哪个文件"）
   - 参数查询（"怎么用"/"参数含义"）

3. **简单操作**：
   - 单文件简单修改（<50 行，逻辑明确）
   - 文档更新（内容已明确）
   - 读取文件、运行命令（无需决策）

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
- **所有文件必须使用 UTF-8 编码（无 BOM）保存**。
  - ⚠️ **严重教训**：曾因编码问题（GBK/UTF-8 混乱）导致文档出现乱码，需回退 Git 历史修复。
  - 编辑器配置：VS Code 默认 UTF-8，确保 `.vscode/settings.json` 中设置 `"files.encoding": "utf-8"`。
  - 验证方法：使用 `file -i <文件名>` (Linux) 或检查编辑器右下角编码显示。

### 文档要求
- 文档清晰、完整、易懂。
- **所有 Markdown 文档必须使用 UTF-8 编码（无 BOM）**，避免中文乱码。

### 测试要求
- 所有代码在 Linux/Raspberry Pi 上可运行。

### Git 仓库管理
- 不进行仓库操作，引导用户操作，保留用户在 commit 信息编辑的自主权。

### 文档同步机制
**核心原则**：代码修改后**立即**同步文档，而非等到"阶段性部分"。

⚠️ **关键提醒**：**每次完成代码修改后，必须立即检查是否需要更新文档！**
- 这不是可选项，而是**强制要求**
- AI 助手在完成代码修改后，**必须主动执行**下方检查流程
- 如果忘记同步文档，用户有权要求重新补充

**文档同步检查流程**（代码修改完成后立即执行）：

#### 第一步：识别修改类型
根据本次修改的性质，判断属于哪种类型：

| 修改类型 | 识别特征（如何判断） | 文档同步动作 |
|---------|---------------------|-------------|
| **配置变更** | • 修改了全局配置文件（被多个模块导入的配置）<br>• 新增配置项或常量定义<br>• 示例：`config.py`, `settings.py` | 更新项目指令文档中的配置章节<br>（如 copilot-instructions.md） |
| **架构调整** | • 修改了模块间依赖关系（import 变更）<br>• 改变数据流或控制流<br>• 修改线程模型、通信机制 | 更新架构总览文档<br>（如 `general_intro_for_ai.md`） |
| **新模块开发** | • 新增 Python 模块（文件夹或独立 .py）<br>• 包含 3+ 个函数或 100+ 行代码<br>• 实现了独立的功能领域 | 创建新的开发历程文档<br>（`[模块名]_journey.md`） |
| **算法优化** | • 修改核心算法逻辑<br>• 性能优化（时间/空间复杂度）<br>• 复杂 bug 修复（涉及设计缺陷） | 更新/创建相关的历程文档<br>（`*_journey.md`） |
| **设计决策** | • 存在 ≥2 种实现方案<br>• 需要权衡利弊（性能/复杂度/可维护性）<br>• 涉及硬件限制、技术选型 | 创建决策记录文档<br>（`[主题]_decision_journey.md`） |
| **陷阱发现** | • 踩坑、调试过程中发现重要经验<br>• 容易误用的 API 或设计缺陷<br>• 硬件/环境相关的特殊问题 | 更新项目指令文档中的<br>"常见问题与陷阱"章节 |

#### 第二步：执行文档同步
根据识别的类型，执行对应的文档更新操作（可能同时匹配多种类型）。

#### 第三步：验证完整性
确认以下问题都有答案：
- ✅ 3个月后重新阅读代码，能否理解设计意图？
- ✅ 其他开发者（或AI）能否通过文档快速上手？
- ✅ 关键的技术决策是否有记录可查？

#### 文档类型与用途
| 文档类型 | 文件命名规范 | 适用场景 | 示例 |
|---------|-------------|---------|------|
| **AI技术文档** | `[主题]_for_ai.md` | 供AI理解的架构、机制说明 | `general_intro_for_ai.md` |
| **开发历程** | `[模块]_journey.md` | 记录开发过程、设计思路 | `autoaim_search_strategy_journey.md` |
| **决策记录** | `[功能]_decision_journey.md` | 多方案对比、技术选型 | `uart_feedback_decision_journey.md` |
| **用户手册** | `[主题].md` | 使用说明、配置指南 | `repl.md` |
| **项目指令** | `copilot-instructions.md` | AI助手的行为准则、配置参考 | `.github/copilot-instructions.md` |

#### 文档膨胀控制
- `*_journey.md` 文档超过 500 行 → 考虑拆分为多个主题文档
- 过时的技术细节 → 移动到 `documents/archive/` 文件夹
- 新阶段开发 → 创建新的 journey 文档，不确定时优先创建

#### 文档自动生成机制
**何时自动创建新的 journey 文档**：

满足以下条件之一时，**主动提示**用户是否创建新的 `*_journey.md` 文档：

1. **新模块开发**：
   - 在 `src/` 下创建新的 Python 模块（新文件夹或独立 .py 文件）
   - 新模块包含 3+ 个函数或 100+ 行代码
   - 触发时机：模块初步完成后（核心功能可运行）

2. **重大重构**：
   - 单次修改影响 3+ 个文件
   - 修改涉及架构调整或设计模式变更
   - 触发时机：重构完成后

3. **复杂 Bug 修复**：
   - 调试过程涉及多个模块交互
   - 发现了重要的设计缺陷或性能陷阱
   - 触发时机：问题解决后

4. **设计决策**：
   - 存在多种实现方案，需要记录选择理由
   - 涉及硬件限制、性能权衡等关键因素
   - 触发时机：方案确定后

**文档命名规范**：
- 模块开发：`[模块名]_implementation_journey.md`（如 `aimassistant_implementation_journey.md`）
- 重构/优化：`[模块名]_[主题]_journey.md`（如 `recognizer_simplification_journey.md`）
- 设计决策：`[功能]_decision_journey.md`（如 `uart_feedback_decision_journey.md`）

**文档模板**（自动生成时使用）：
```markdown
# [功能/模块名称] 实现/决策记录

## 背景与目标
- **开发时间**：YYYY-MM-DD
- **相关版本**：vX.X
- **涉及模块**：列出修改的文件

## 核心设计
[描述主要设计思路、架构选择]

## 实现细节
[关键代码逻辑、算法说明]

## 遇到的问题与解决
[踩坑记录、调试过程]

## 性能/测试验证
[性能指标、测试结果]

## 未来优化方向
[已知限制、待改进点]
```

**提示用户的话术示例**：
> "注意到您刚完成了 [模块名] 的开发，涉及 [文件列表]。是否需要我创建 `[模块名]_implementation_journey.md` 文档，记录设计思路和实现细节？这将帮助未来的开发和 AI 理解上下文。"

#### 文档自动更新提示机制
**何时主动提示用户更新现有 journey 文档**：

满足以下条件时，**主动提醒**用户是否需要更新对应的 journey 文档：

1. **修改已有模块且存在对应 journey 文档**：
   - 修改 `src/bot/gimbal.py` → 检查是否存在 `gimbal_*_journey.md`
   - 修改 `src/aimassistant/` → 检查是否存在 `aimassistant_*_journey.md`
   - 修改 `src/recognizer.py` → 检查是否存在 `recognizer_*_journey.md`

2. **修改涉及重要设计变更**：
   - 修改核心算法或数据结构
   - 改变硬件控制逻辑（如云台控制范围）
   - 修复复杂 bug 或性能问题

3. **触发时机**：
   - 代码修改完成后立即检查
   - 在用户提交代码前提醒

**检查流程**：
1. 识别修改的模块名称（从文件路径提取，如 `gimbal`, `aimassistant`, `recognizer`）
2. 在 `documents/` 和 `documents/archive/` 中搜索 `[模块名]*journey.md`
3. 如果找到对应文档，提示用户是否需要更新

**提示话术示例**：
> "注意到您修改了 `src/bot/gimbal.py`，发现存在相关文档 `documents/archive/gimbal_360_implementation_journey.md`。是否需要我在该文档中添加本次修改的记录（pitch/yaw 协同控制逻辑优化）？"

**更新内容建议**：
- 在文档的"实现细节"或"遇到的问题与解决"章节追加内容
- 标注更新时间和修改摘要
- 如果是重大变更，考虑创建新的 journey 文档而非更新旧文档

## 用户意图理解与确认机制
### 何时必须提问
1. **需求模糊**：用户说"优化一下"、"改进一下" → 确认具体优化方向
2. **多种实现方式**：如阻塞 vs 非阻塞 → 确认用户偏好和使用场景
3. **架构影响**：变更会影响多个模块 → 确认影响范围是否可接受
4. **上下文矛盾**：用户回答与之前对话不符 → 确认是修正还是新需求
5. **关键参数缺失**：如硬件参数、性能指标 → 询问具体数值

### 提问技巧
- ✅ **提供具体选项**（A/B/C），而非开放式问题
- ✅ **说明利弊**：每个选项的优缺点
- ✅ **用示例代码**：澄清理解，避免歧义
- ❌ **避免连续多问**：一次最多问 2-3 个相关问题

## 渐进式开发原则
### 触发条件（满足任一即启用）
- 任务涉及 **3+ 步骤**
- 任务需要修改 **3+ 文件**
- 任务包含 **"设计 → 实现 → 测试"** 完整流程

### 实施步骤
1. 接到复杂任务后，使用 `manage_todo_list` 工具列出实施步骤
2. 每完成一步，标记为 `completed` 并验证功能
3. 下一步开始前，确认上一步无问题
4. 鼓励 **"最小可用版本"** 思维：先实现核心功能，再逐步完善

### 不适用场景
- 单文件简单功能（如添加一个工具函数）
- 明确的单一任务（如"修复某个 bug"）

## 显式思考过程
- 回答有显式思考过程，避免盲目生成代码。
- 复杂任务自动调用 sequential thinking 工具（见"自动思考触发规则"章节）。

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
AIM_LOST_TARGET_TIMEOUT_FRAMES = 5   # 连续无目标的帧数阈值（触发搜索）
AIM_CONTROL_FREQUENCY = 20           # 自瞄控制频率（Hz）
AIM_SEARCH_FOV_COVERAGE = 0.7        # 搜索步进占视野角度的比例
AIM_SEARCH_DIRECTION = 1             # 搜索方向（1=右，-1=左）
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

### 性能敏感区域识别与优化 ⚡

#### 如何识别性能敏感模块？
满足以下**任一特征**的模块属于性能敏感区域，修改时需特别注意：

1. **高频调用**：
   - 被主循环或控制循环频繁调用（>10 Hz）
   - 示例：自瞄系统控制循环（20 Hz）、视觉推理循环

2. **实时性要求**：
   - 响应延迟直接影响功能表现
   - 示例：云台控制、底盘运动控制、实时目标识别

3. **线程密集**：
   - 包含多线程、异步操作、共享资源
   - 示例：双线程视觉识别、串口后台接收线程

4. **I/O 密集**：
   - 频繁的硬件 I/O、网络 I/O、文件 I/O
   - 示例：串口通信、摄像头采集、模型推理

#### 当前项目中的性能敏感模块（示例）
以下仅为**当前项目的示例**，新模块按上述特征判断：

- **视觉识别模块**：双线程设计，推理频率要求，已优化 ONNX 推理
- **自瞄系统**：目标选择器高频调用（20 Hz），角度计算需快速且精确
- **串口通信**：后台接收线程需实时响应，已实现非阻塞 + 双队列

#### 性能优化原则
- ✅ **修改前评估**：评估是否引入阻塞操作（睡眠、I/O 等待、复杂计算）
- ✅ **添加逻辑前思考**：考虑是否影响实时性（控制频率、响应延迟）
- ⚠️ **非热路径优化**：配置加载、日志输出等不需过度优化
- ⚠️ **优先级原则**：优先保证功能正确性，再优化性能

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
### REPL 优先原则 🔧
**新硬件控制功能必须先在 REPL 中验证**，再集成到主程序。

#### 强制使用 REPL 的场景
1. 添加新的硬件控制函数（云台、底盘、发射器）
2. 修改串口通信协议或命令格式
3. 验证参数范围（如速度限制、角度限制）
4. 调试硬件异常行为

#### REPL 验证流程
1. 启动 REPL：`python src/repl.py`
2. 发送原始命令，观察硬件响应和日志输出
3. 确认功能正常后，再将逻辑封装到 `src/bot/` 模块
4. 最后集成到主程序或技能系统

### 标准调试流程
1. **串口测试**：`python src/repl.py` → 发送 `command;` 检查响应
2. **技能验证**：主程序中绑定测试键，观察日志输出
3. **视觉调试**：调用 `Recognizer.imshow()` 查看检测结果

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
### 必检项（每次提交必须完成）
- [ ] **类型提示**：所有公共函数有类型提示（`typing` 模块）
- [ ] **命名规范**：函数用 `动词_名词`，变量用 `小写下划线`，私有加 `_` 前缀
- [ ] **文件编码**：UTF-8（无 BOM），避免中文乱码
- [ ] **路径规范**：避免 Windows 特定路径（如 `C:\`），使用 Linux 路径（如 `/dev/ttyUSB0`）
- [ ] **文档同步**：更新相关 `*_journey.md` 或 `current_progress.md`（见"文档同步机制"）

### 建议检查项（根据修改内容选择）
- [ ] **参数验证**：硬件控制代码添加参数范围验证和注释
- [ ] **错误处理**：添加适当的 try-except 和日志输出（见"错误处理规范"）
- [ ] **性能验证**：性能敏感模块确认无阻塞操作
- [ ] **配置管理**：新配置项添加到 `src/config.py`
- [ ] **功能验证**：通过 REPL 或主程序验证功能正常
- [ ] **日志检查**：确认日志输出无异常

### 错误处理规范 🛡️
以下场景**必须**有错误处理：

1. **硬件控制**：参数范围验证
```python
def set_chassis_speed_3d(x: float, y: float, z: float):
    if not -3.5 <= x <= 3.5:
        raise ValueError(f"x speed {x} out of range [-3.5, 3.5]")
    # ...
```

2. **外部调用**：异常捕获 + 日志
```python
try:
    result = model.run(...)
except Exception as e:
    LOG.error(f"YOLO inference failed: {e}")
    return None
```

3. **资源操作**：确保清理
```python
try:
    # 文件/线程操作
finally:
    # 清理资源
```

# 常见问题与陷阱

## 如何识别和记录新陷阱？
遇到以下情况时，应在本章节添加新的陷阱记录：

1. **调试耗时 >30 分钟**：问题不明显，容易被忽略
2. **违反直觉的行为**：代码逻辑看似正确，但实际运行异常
3. **硬件/环境相关**：特定硬件、操作系统、Python 版本导致的问题
4. **API 误用**：官方文档不清晰或容易误解的接口
5. **性能陷阱**：不当使用导致性能显著下降

**记录格式**：
```markdown
## [问题简短描述]
- **症状**：用户观察到的现象
- **原因**：根本原因分析
- **解决方案**：具体操作步骤
- **预防措施**：如何避免再次出现
```

---

## 当前项目陷阱案例库

### 技能按键不触发
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

## 云台控制角度错误 ⚠️
- **Pitch 轴（俯仰轴）**：
  - ❌ **错误**：使用 `% 360` 归一化（pitch 不能无限旋转）
  - ✅ **正确**：范围限制 `[-55°, 55°]`（相对角度）或 `[-25°, 30°]`（绝对角度）
  - **参考零点**：pitch=0° 时云台指向水平面平行
  - **机械限制**：受云台结构限制，超出范围会导致硬件异常
  
- **Yaw 轴（偏航轴）**：
  - ✅ **支持无限旋转**：滑环设计支持 360° 连续旋转
  - ⚠️ **单次指令限制**：下位机单次相对角度指令限制 ±55°
  - **大角度旋转**：需要分步执行，选择最短路径（归一化到 `[-180°, 180°)`）

- **协同控制陷阱**：
  - ❌ **错误**：pitch 和 yaw 分开调用 `_move_gimbal()`，导致无法同步运动
  - ✅ **正确**：第一次调用同时发送 pitch 和 yaw 参数，后续分步只发送 yaw

- **参考文档**：`documents/archive/gimbal_360_implementation_journey.md`

## 视觉识别帧率低
- 检查 `rec.get_fps_info()` 输出。
- 降低模型复杂度或图像分辨率。
- 确认双线程正常运行（采集与推理分离）。

## 文档编码异常（中文乱码）
- **症状**：Markdown 文档中文显示为乱码（如 `鍏ㄥ眬閰嶇疆`）。
- **原因**：文件被保存为 GBK 或其他非 UTF-8 编码。
- **解决方案**：
  1. 检查文件编码：VS Code 右下角查看编码显示。
  2. 转换为 UTF-8：点击编码 → "通过编码重新打开" → 选择原编码 → "通过编码保存" → UTF-8。
  3. 批量修复：曾使用 `tools/fix_encoding.py` 统一转换（已移除，历史参考）。
- **预防措施**：
  - 确保 VS Code 设置 `"files.encoding": "utf-8"`。
  - 提交前检查 `git diff` 是否出现乱码。
  - 避免使用 Windows 记事本编辑文档（可能保存为 GBK）。

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

# 文档关联机制 📚
## 核心文档索引
为了保持 `copilot-instructions.md` 的简洁性，详细的技术文档、设计决策和规范分散在 `documents/` 目录中。AI 助手应根据任务需求，动态查阅相关文档。

### 文档分类与用途

#### 架构与机制文档
- **`documents/general_intro_for_ai.md`**：项目架构总览
  - 何时阅读：架构级任务、多模块交互、首次接触项目
  - 内容：三层架构、模块职责、数据流、设计模式
  
- **`documents/aimassistant_intro_for_ai.md`**：自瞄系统设计
  - 何时阅读：涉及自瞄、目标选择、视觉识别
  - 内容：自瞄算法、目标选择器、搜索策略

#### 编码规范文档
- **`documents/coding_style_guide_for_ai.md`**：编码风格指南
  - 何时阅读：**生成任何代码前必读**
  - 内容：命名规范、类型提示、注释风格、错误处理、设计模式
  - 关键要点：
    - 命名：snake_case 函数/变量，动词_名词格式
    - 类型提示：Python 3.10+ 新语法，公共函数 100% 覆盖
    - 注释：口语化可接受，Emoji 仅限注释/文档（禁止命令行输出）
    - 硬件控制：必须验证参数范围

#### 开发历程文档
- **`documents/*_journey.md`**：开发过程记录
  - 何时阅读：涉及对应模块的修改、优化、bug 修复
  - 内容：设计思路、实现细节、踩坑记录、性能分析
  - 示例：
    - `autoaim_search_strategy_journey.md`：自瞄搜索策略实现
    - `recognizer_simplification_journey.md`：视觉识别简化过程
    - `uart_feedback_decision_journey.md`：串口反馈机制设计决策

#### 用户手册文档
- **`documents/repl.md`**：REPL 调试工具使用说明
  - 何时阅读：指导用户使用 REPL 工具、调试串口通信
  - 内容：启动方法、命令格式、调试流程

### 文档查阅优先级
根据任务类型，按以下优先级阅读文档：

#### 生成代码任务
1. **必读**：`documents/coding_style_guide_for_ai.md`（编码风格）
2. **建议**：对应模块的 `*_for_ai.md` 或 `*_journey.md`（了解设计）
3. **兜底**：`documents/general_intro_for_ai.md`（理解架构）

#### 架构设计任务
1. **必读**：`documents/general_intro_for_ai.md`（架构总览）
2. **建议**：相关的 `*_journey.md`（历史决策）
3. **参考**：`documents/coding_style_guide_for_ai.md`（规范约束）

#### 问题诊断任务
1. **必读**：相关模块的 `*_journey.md`（已知问题）
2. **建议**：`copilot-instructions.md` 的"常见问题与陷阱"章节
3. **参考**：`documents/general_intro_for_ai.md`（模块交互）

### 文档更新机制
遵循"文档同步机制"章节的要求，代码修改后立即更新相关文档。

---

# 参考资料（快速索引）
- **架构说明**：`documents/general_intro_for_ai.md`
- **编码规范**：`documents/coding_style_guide_for_ai.md` ⭐ **生成代码前必读**
- **自瞄系统**：`documents/aimassistant_intro_for_ai.md`
- **REPL 工具**：`documents/repl.md`

## 工具模块优先原则 🔧

### 新功能开发前必检
添加新的工具函数前，**必须先检查** `src/utils.py` 是否已有类似功能：

1. **搜索现有函数**：
   ```bash
   grep -r "def function_name" src/utils.py
   ```

2. **检查功能重复**：
   - 图像处理 → 优先查看 `utils.py`
   - 数据转换 → 检查是否已有通用实现
   - 数学计算 → 避免重复造轮子

3. **决策流程**：
   ```
   需要新工具函数？
   ├─ 是否已在 utils.py 中？
   │  ├─ 是 → 直接导入使用
   │  └─ 否 → 继续检查
   │
   ├─ 是否为通用功能？
   │  ├─ 是 → 添加到 utils.py
   │  └─ 否 → 添加到模块内部
   │
   └─ 是否需要优化现有函数？
      ├─ 是 → 更新 utils.py + 同步文档
      └─ 否 → 创建新函数
   ```

### 禁止重复定义
❌ **错误示例**（重复定义）：
```python
# recognizer.py
def adjust_gamma(image, gamma=1.0):
    # ... 与 utils.py 中的函数相同

# data_collector.py
def adjust_gamma(image, gamma=1.0):
    # ... 再次重复定义
```

✅ **正确示例**（导入使用）：
```python
# recognizer.py
from utils import adjust_gamma

# data_collector.py  
from utils import adjust_gamma
```

### 工具模块规范

#### 适合放入 `utils.py` 的函数
- ✅ 图像预处理（gamma、直方图均衡、降噪）
- ✅ 数据类型转换（np.ndarray ↔ list、角度归一化）
- ✅ 数学计算（距离、角度、坐标变换）
- ✅ 文件操作（路径处理、配置读取）
- ✅ 被 2+ 模块使用的功能

#### 不适合放入 `utils.py` 的函数
- ❌ 模块特定逻辑（如云台控制、串口协议解析）
- ❌ 业务逻辑（技能管理、自瞄算法）
- ❌ 硬件接口封装（特定于某个模块）

### 历史教训案例

**案例**: `adjust_gamma()` 函数重复定义（2025-10-12）
- **问题**: 在 `utils.py`、`recognizer.py`、`data_collector.py` 中重复定义
- **影响**: 维护成本高、类型提示不一致
- **解决**: 统一使用 `utils.py` 中的定义，其他模块导入
- **详见**: `documents/archive/gamma_function_refactoring_journey.md`

### 提交前检查清单（补充）
在原有检查清单基础上，添加：

- [ ] **工具函数复用**：新增函数前检查 `utils.py` 是否已有
- [ ] **重复代码检测**：使用 `grep -r "def function_name"` 检查重复定义
- [ ] **导入路径正确**：确保 `from utils import ...` 可正常工作
