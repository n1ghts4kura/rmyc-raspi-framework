---
title:  当前项目状态总览
date:   2025-11-22
status: active
maintainer: LLMs (GPT 5.0/5.1, Claude Sonnet 4.0 / Haiku, Gemini 3)
category: none
---

## 1. 版本与阶段概览

- 当前主开发分支：`dev_v1_1_re`
- 当前大版本: v1.1
- 当前大版本任务：聚焦于实现基础的自瞄功能闭环，搭建起核心模块间的交互与数据流。除此之外，还包括部分基础设施完善，如 REPL 调试工具与文档体系初步搭建。
- 当前小版本: v1.1re
- 当前小版本任务：在已经基本完善的 v1.1 功能基础上，重构文档系统与 LLM 协作流程，确保文档能够更好地支持后续功能扩展与维护工作。

> 本节应在每次重要里程碑完成后手动更新，以保持对「当前阶段」的准确描述。你**应该**提醒维护者在每次完成重要任务后更新本节内容。

---

## 2. 功能完成度概览（按子系统）

> 说明：以下为高层概览，具体实现细节请参考对应模块源码与未来的 `*_intro.md` / `*_journey.md` 文档。

### 2.1 通信与硬件抽象层（`src/bot/`）

- 主要模块：`conn.py`、`robot.py`、`chassis.py`、`gimbal.py`、`blaster.py`、`sdk.py`、`game_msg.py` 等。
- 当前状态（按 v1.1re 规划粗略评估）：
  - 串口连接与基础命令发送：**基础功能已实现，需在更多场景下回归验证**。
  - 底盘 / 云台 / 发射器基础控制：**接口已封装并在 REPL / 简单脚本下通过初步验证**。
  - 与 RoboMaster SDK 协议兼容性：**常用指令已对接，边缘指令与异常场景仍待补充验证**。

### 2.2 视觉识别（`src/recognizer.py` + `model/`）

- 模型与框架：
  - YOLOv8 ONNX / PyTorch / NCNN 模型位于 `model/` 目录。
  - 推理逻辑集中在 `src/recognizer.py` 中。
- 当前状态（按 v1.1re 规划粗略评估）：
  - 模型加载与基本推理：**在开发环境与树莓派上均已跑通基础链路**。
  - 在树莓派上推理性能（FPS / 延迟）：**已可稳定达到 4FPS 左右，仍有进一步优化空间**。

### 2.3 自瞄系统（`src/aimassistant/` + `src/skill/autoaim.py`）

- 主要模块：`aimassistant/angle.py`、`aimassistant/pipeline.py`、`aimassistant/selector.py`、`skill/autoaim.py`。
- 当前状态（按 v1.1re 规划粗略评估）：
  - 从识别结果到目标选择（selector）逻辑：**v1 策略已实现并可在实机上工作**。
  - 角度计算与云台控制接口（angle + pipeline）：**已与 `bot/gimbal` 打通，形成完整控制链路**。
  - 实机自瞄闭环效果：**已可在有限场景下稳定运行，泛化与鲁棒性仍待更多测试**。

### 2.4 技能系统（`src/skill/`）

- 主要模块：`skill/manager.py`、`skill/base_skill.py`、`skill/example_skill.py` 等。
- 当前状态（按 v1.1re 规划粗略评估）：
  - 技能注册与触发机制：**`SkillManager` / `BaseSkill` 已就绪，可支持键盘/指令触发技能**。
  - 示例技能：**已包含自瞄等示例技能，可作为新技能实现的参考模板**。

### 2.5 REPL 调试工具（`src/repl.py`）

- 作用：提供交互式命令行，用于快速下发控制命令、调试串口 / 硬件行为。
- 当前状态（按 v1.1re 规划粗略评估）：
  - 在开发机上可用性：**仅用于代码编辑与静态检查，不在 Windows 上实际运行**。
  - 在树莓派与实机环境中的可用性：**已作为日常 UART / SDK 调试的推荐工具使用**。

---

## 3. 运行环境与测试验证状态

> 本节用于描述「代码已经在什么环境下被验证过」，便于评估当前可靠性。

### 3.1 开发与目标运行环境

- 开发环境：
  - 操作系统：Windows（开发 / 编辑代码）。
  - Python 版本：3.10+（具体版本以 `requirements.txt` 为准）。
- 目标运行环境：
  - 硬件：树莓派 + DJI RoboMaster S1/EP。
  - 操作系统：Linux（Raspberry Pi OS 或兼容发行版）。

### 3.2 当前验证情况（请按实际情况补充）

- 在开发机上：
  - `demo_vision.py`：_TODO: 是否已运行，效果如何_
  - `src/main.py`：_TODO: 是否已运行，整体验证程度_
- 在树莓派上：
  - 串口通信与基础控制：_TODO_
  - 视觉推理与自瞄流程：_TODO_
- 自动化测试：
  - 单元测试 / 集成测试：当前主要依赖手工测试，尚未建立系统化自动化测试体系。_如有变化请更新_

---

## 4. 已知问题、限制与关键技术债

> 本节只列出高优先级的限制与风险，详细过程建议放入对应的 `*_journey.md` 文档中。

- 示例占位（请根据实际情况调整）：
  - 自瞄效果目前仅在有限场景（特定光照 / 目标形式）下验证，泛化能力有待评估。
  - 云台 pitch/yaw 的机械 / 角度限制尚需在实机环境下进一步标定，部分边界角可能存在风险。
  - 在树莓派上的推理性能（FPS / 延迟）尚未达到最终目标，后续需要针对性优化。
  - 文档体系仍在搭建阶段，大部分 `*_intro.md` / `*_journey.md` 目前仅处于规划状态。

---

## 5. 文档与工具当前状态

### 5.1 文档状态

- 已存在核心文档：
  - `docs/index.md`：文档导航入口与命名 / 匹配规则说明（已挂载模块 intro 与 REPL 指南入口）。
  - `docs/status.md`：当前项目状态快照（本文档）。
  - `.github/copilot-instructions.md`：面向 LLM 的行为与架构说明。
  - `docs/intro/aimassistant_intro.md`：自瞄系统设计说明（v1.1re 阶段已完成初版）。
  - `docs/intro/vision_intro.md`：视觉识别模块说明（已完成初版）。
  - `docs/intro/skill_intro.md`：技能系统说明（已完成初版）。
  - `docs/intro/bot_intro.md`：机器人硬件抽象层说明（已完成初版）。
  - `docs/guide/repl.md`：UART 异步 REPL 串口调试工具使用说明（已对齐树莓派运行环境与新文档结构）。
  - `docs/journey/v1_0_history.md`：v1.0 阶段整体开发历程复盘（已存在，内容可继续按需补充）。
  - `docs/journey/aimassistant_journey.md`：自瞄系统从最初版本到当前实现的演进记录（已存在，适合作为自瞄相关重构/优化的背景材料）。
  - `docs/journey/performance_journey.md`：性能优化相关的重要尝试与经验记录（已存在，偏横切主题）。
  - `docs/journey/vision_recognition_journey.md`：视觉识别模块演进记录（已创建 skeleton，后续根据实际演进逐步补齐）。
  - `docs/journey/uart_communication_journey.md`：UART 通信与 SDK 协议演进记录（已创建 skeleton）。
  - `docs/journey/gimbal_control_journey.md`：云台控制与 360° 旋转演进记录（已创建 skeleton）。
  - `docs/journey/skill_system_journey.md`：技能系统与自动化行为演进记录（已创建 skeleton）。
- 计划中的重要文档（示例）：
  - `docs/general_intro.md`：项目整体架构与设计原则总览。
  - 更多模块对应的 `*_journey.md`：记录设计历程与关键决策（现已包含通信 / 视觉 / 云台 / 技能等多条主线，后续新增时应在此同步登记）。
- 当前文档策略：
  - 以 `index.md` + `status.md` 作为导航与状态骨架；
  - 各模块 `intro/*.md` 作为事实来源，`journey/*.md` 记录演进与坑点，`guide/*.md` 记录具体操作；
  - 其他详细文档在此基础上由 LLM 按需生成和补充。

### 5.2 工具状态

- `src/repl.py`：
  - 主要用于交互式调试与快速试验，适合在接入新硬件指令前先在 REPL 中验证。
  - 具体可用性与常见用法：_TODO 建议在 `repl.md` 中详细说明_
- `tools/` 目录下脚本：
  - `install_cpu_performance_service.sh` / `set_cpu_performance.sh` / `uninstall_cpu_performance_service.sh` / `verify_power.sh`
  - 主要用于在树莓派上配置 CPU 性能模式与供电验证，推荐在部署或性能测试前使用。具体步骤：_TODO 可在未来文档中补充_

---

## 7. 维护与更新约定

- 维护者信息：
  - 当前 LLM 协作者：GPT 5.0/5.1、Claude Sonnet 4.0 / Haiku、Gemini 3（具体能力与分工视实际工具而定）。
  - 人类项目所有者：**n1ghts4kura**
  - 修改者：所有团队成员
- 更新策略：
  - 建议在以下时机更新本 `status.md`：
    - 完成一个主要版本或里程碑（例如 v1.1 功能冻结）。
    - 完成一次重要实机测试（例如大规模自瞄测试）。
    - 进行重大架构调整或性能优化，导致上述状态信息发生明显变化。
- 使用约定：
  - 其他文档或 LLM 在需要了解「项目当前真实状态」时，应优先参考本文件；
  - 如发现本文件与实际情况明显不符，应优先更新本文件，再基于最新状态生成或修改其他文档。
