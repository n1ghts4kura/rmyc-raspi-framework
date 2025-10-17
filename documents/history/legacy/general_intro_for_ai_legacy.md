---
title: RMYC Raspi Framework 架构总览（Legacy）
version: 2025-10-18
status: draft
maintainers:
  - Copilot Assistant
  - GitHub Copilot
category: guide
last_updated: 2025-10-18
related_docs:
  - new_docs/general_intro_for_ai.md
  - documents/history/legacy/aimassistant_intro_for_ai_legacy.md
  - documents/reference/coding_style_guide_for_ai.md
llm_prompts:
  - "用于快速了解框架层次结构、串口与技能系统协作方式"
---

# RMYC Raspi Framework 架构总览（Legacy）

> **适用角色**：算法、嵌入式、文档维护者、AI 协作者。
> **前置条件**：熟悉 RoboMaster SDK 基础操作，了解树莓派部署环境。
> **阅读收益**：在架构级任务、跨模块重构或文档迁移时快速掌握系统结构与关键依赖。

## 背景与适用范围

- **赛事背景**：RMYC（机甲大师空地协同对抗赛）采用 4v4 战术射击赛制，机器人需要在自动阶段完成自瞄、护甲削弱等关键动作。
- **框架目标**：
  - 在树莓派侧构建统一技能框架，集中调度底盘、云台、发射器等子系统。
  - 通过 UART 将键鼠事件与机器人状态串接起来，支撑实时技能触发。
  - 基于 YOLO + OpenCV 的视觉模块为自瞄提供目标识别与角度估计能力。
- **使用场景**：
  - 为新协作者（人类或 LLM）提供项目入门指引。
  - 在评估跨模块改动、性能优化或重构时梳理依赖关系。
  - 与 `new_docs/general_intro_for_ai.md` 对照，识别新版文档与 Legacy 记录的差异。

## 核心内容

### 框架层次结构

```
┌─────────────────────────────────────────────┐
│          应用层 (Application Layer)         │
│  • main.py: 主循环、事件分发、技能调度      │
│  • repl.py: 交互式调试工具                  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│        业务逻辑层 (Business Logic Layer)    │
│  • skill/: 技能框架（定义、管理、执行）     │
│  • aimassistant/: 自瞄系统（目标选择）      │
│  • recognizer.py: 视觉识别（YOLO 推理）     │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│      硬件抽象层 (Hardware Abstraction)      │
│  • bot/conn.py: 串口通信（队列、线程）      │
│  • bot/gimbal.py: 云台控制                  │
│  • bot/chassis.py: 底盘运动                 │
│  • bot/blaster.py: 发射器控制               │
│  • bot/game_msg.py: 赛事消息解析            │
└─────────────────────────────────────────────┘
```

### 技术选型概览

| 技术领域 | 选型 | 主要理由 |
| --- | --- | --- |
| 开发语言 | Python 3.10+ | 语法直观、生态成熟、快速迭代 |
| 视觉识别 | YOLO + OpenCV | 预训练模型丰富，易于移植至树莓派 |
| 通讯协议 | UART 串口 | 硬件支持广泛，可靠性高 |
| 调试工具 | Prompt Toolkit REPL | 支持彩色输出、异步交互、命令历史 |
| 日志系统 | 自研 `logger.Logger` | 单例模式、等级过滤、与技能系统解耦 |

### 核心数据流与接口

```
键鼠事件 → 串口传输 → bot/game_msg.process() → SkillManager
                                                 ↓
                               invoke_skill_by_key / cancel_skill_by_key
                                                 ↓
                               BaseSkill（线程执行技能逻辑）
                                                 ↓
                               底盘 / 云台 / 发射器命令
                                                 ↓
                               串口发送至机器人执行
```

- **输入源**：客户端透传的键鼠事件与赛事消息。
- **业务中枢**：`skill/manager.py` 调度技能生命周期，确保互斥关系与异常兜底。
- **硬件抽象**：`bot/` 模块封装串口协议、姿态控制与发射逻辑，降低上层复杂度。
- **视觉环节**：`recognizer.py` 使用双线程模型（采集 + 推理），将最新识别结果缓存在内存中供自瞄调用。

### 性能敏感区域（⚡）

- **识别标准**：
  1. 调用频率超过 10 Hz。
  2. 对实时性高度敏感（如闭环控制）。
  3. 涉及多线程或共享资源。
  4. 需要频繁硬件 I/O。
- **当前高优先级模块**：视觉识别线程、自瞄目标选择器、串口收发服务。
- **执行守则**：
  - 修改前评估潜在阻塞点与 CPU 占用。
  - 优先保证正确性，再规划优化方案。
  - 非热路径（日志、配置）无需过度微调。

### 模块职责速览（源自 `src/`）

- `main.py`：应用入口，初始化串口与技能，驱动主循环。
- `logger.py`：彩色分级日志，提供 DEBUG 开关。
- `recognizer.py`：摄像头采集 + YOLO 推理线程。
- `repl.py`：Prompt Toolkit 驱动的调试终端。
- `bot/`：串口连接、云台/底盘/发射器控制、赛事消息解析。
- `skill/`：技能定义、管理、执行模板。
- `model/`：存放推理模型与辅助脚本。
- `test_*.py`：快速验证核心路径的轻量测试脚本。

## 操作步骤（建议流程）

1. **建立上下文**：先阅读 `new_docs/index.md` 与本文件，掌握模块边界与依赖。
2. **聚焦模块**：依据任务域跳转至 `guide/` 或 `history/` 的对应文档，确认历史决策。
3. **评估影响**：识别是否触及性能敏感区域或跨模块依赖，提前规划验证方案。
4. **同步文档**：若变更架构或接口，参照 `new_docs/principles.md` 在索引与相关文档中标记状态与责任人。
5. **复核成果**：通过 REPL、测试脚本或实机验证确认功能与性能目标，记录验证结论。

## 验证与状态

- `last_updated` 已更新至 2025-10-18，待 Legacy 资料迁移完成后将状态从 `draft` 调整为 `reviewed`。
- 建议与 `new_docs/general_intro_for_ai.md` 对照阅读，确保后续迁移不丢失关键信息。
- 下一步：在 `new_docs/index.md` 添加该文档入口，并确认 Legacy 内容是否需要拆分或归档。

## 附录与引用

- **相关指引**：`new_docs/general_intro_for_ai.md`、`documents/reference/coding_style_guide_for_ai.md`
- **历史记录**：`documents/history/legacy/aimassistant_intro_for_ai_legacy.md`、`documents/history/gimbal_360_implementation_history.md`
- **工具手册**：`documents/guide/repl.md`、`documents/guide/utils_module_for_ai.md`
- **下一步行动**：更新索引、规划 Legacy → New Docs 的迁移路径。

---
如发现内容与现状不符，请在 24 小时内更新 `new_docs/problems.md` 并通知维护人执行同步。
