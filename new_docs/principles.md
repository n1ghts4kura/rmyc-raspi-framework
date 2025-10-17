---
title: 文档优化原则（共识草案）
version: 2025-10-17
status: draft
maintainers:
  - Copilot Assistant（临时）
---

# 文档优化原则（共识草案）

> 背景：重新通读 `documents/`（含 `archive/`）与 `new_docs/` 下全部 Markdown 文档后，总结的统一改进准则。原则吸收《Zen of Python》的核心理念（简洁、明确、易读），并以“必须遵守 / 建议采纳”区分执行优先级。原 “Journey” 文档统一称为 “History” 文档，所有命名与引用须随之更新。

## ✅ 必须遵守的原则

**M0. 实时时间确认**  
在每次启动协作或“vibe-coding”前，助手必须向实际编码者询问并记录当下真实日期（格式 `YYYY/MM/DD`），确保 History 记录与代码时间轴一致。

**M1. 文档同步闭环**  
所有代码、配置、硬件参数与流程变化都要同步更新相关文档与状态标记；若尚未同步，应在文档中显式写明 `PENDING` 并列入行动清单。未完成同步时不得宣称完成。

**M2. 分类体系（无 Decision 类）**  
统一分类：`guide`（操作指南）、`history`（历史记录与复盘）、`reference`（接口/协议/配置）、`ops`（计划排程）、`culture`（团队理念）。每篇文档必须在 Front Matter 中声明分类。

**M3. 作者实名责任制**  
凡对文档进行实质性改动的编码者，需在 Front Matter 的 `maintainers` 字段留下姓名或代号，确保责任可追溯。

**M4. 中央索引 `new_docs/index.md`**  
改用 `new_docs/index.md` 作为唯一索引，列出文档→分类→状态→维护人→更新时间；LLM 与成员均以此为入口。

**M5. 引导式知识地图**  
在 `new_docs/index.md` 中提供“概览 → 分类 → 文档”的导航图或结构化列表，并链接核心 History / Guide 文档。

**M6. 结构分层一致性**  
所有文档采用统一章节结构：背景与适用范围 → 核心内容 → 操作步骤 → 验证与状态 → 附录/引用，保证阅读路径清晰。

**M7. 模块化与粒度控制**  
坚持“一篇文档聚焦一个主线主题”；跨主题内容拆分成独立文档并互相引用。大段叙述需要转化为要点或表格。

**M8. 术语与命名统一**  
术语、变量、指令必须与 `coding_style_guide_for_ai.md` 和 `config.py` 保持一致；新增术语需先更新术语表并给出中英对照。

**M9. 变更动机与验证透明**  
每项改动需说明动机、风险、验证方式与结果；若验证未完成，标记 `PENDING` 并写明负责人和预计时间。

**M10. 引用链闭环**  
关键结论必须附带源码、配置或历史记录的链接；相关 `guide` 与 `history` 之间互相引用，形成完整链路。

**M11. 行动导向输出**  
文档结尾列出“立刻可执行步骤 / 风险提醒 / 验收标准 / 预计耗时”，确保读者拿到文档即可执行。

**M12. 模板化撰写与签名**  
在 `documents/templates/` 维护分类模板；所有文档在重写或新增时必须引用模板，并在 Front Matter 中补齐分类、状态、维护人、更新时间。

**M13. 周期审查 + 时间校对**  
每两周执行一次文档审查冲刺，核对状态、分类与引用，同时检查最近协作是否记录真实日期；审查结果写入 `new_docs/problems.md`。

**M14. 文档同步稽核脚本（保留）**  
经权衡后继续保留：开发脚本检测状态标记、分类标签、链接有效性与 Front Matter 完整性；在日常流程中执行，保证同步质量。

**M15. 冲突快速修复流程**  
若发现文档互相矛盾，24 小时内召集维护人确认结论，并同步更新受影响文档、`new_docs/problems.md` 与 `new_docs/index.md`。

**M16. 角色视角提示**  
文档首屏需标注适用角色（算法/硬件/运维/管理）、必备权限与准备条件，帮助读者快速判断是否继续阅读。

**M17. 静态可视化要求**  
允许使用流程图、时序图、示意图，但限定为静态图或 Mermaid 文本，不得引入视频/音频；图像统一放在 `documents/assets/`。

**M18. Front Matter 元数据规范**  
所有 Markdown 文档必须使用 `---` 包裹的 Front Matter，至少包含 `title`、`version`、`status`、`maintainers`、`category`、`last_updated` 字段；主体内容紧随其后。

**M19. LLM 协作提示词库**  
在 `new_docs/index.md` 维护“LLM 提示词”段，收录不同任务的高质量提示语，每次原则或流程变更后同步更新。

**M20. 交付前现实时间复核**  
在提交任何成果前，确认最新实际日期和时间已写入相关 History 文档与索引，确保时间线一致。

**M21. 历史时间线维护**  
`history` 分类文档需按真实时间顺序记录事件；若回溯修改旧条目，需保留原数据并注明修订者与日期。

**M22. 手动校对窗口**  
大规模文档更新后需安排人工校对，逐段审查语言清晰度与术语一致性，可邀请非作者进行可读性评估。

**M23. YAML 元数据扩展**  
在 Front Matter 中可按需扩展 `related_docs`、`source_code_paths`、`llm_prompts` 等字段，增强导航与追溯能力。

**M24. 工具手册与作者认领**  
编写 `new_docs/tools_guide.md` 说明常用编辑/比对/可视化工具，并要求作者在使用新工具时更新该文档并签名。

**M25. 文档保全与备份策略**  
对高价值文档建立离线备份清单，记录备份位置与轮换频率，防止单点故障造成资料遗失。

## 💡 建议采纳的原则

**A1. 文档影响度评级**  
在 `new_docs/index.md` 中标注 High / Medium / Low 影响度，优先复审高影响文档。

**A2. 维护人轮值制度**  
为各分类设定轮值表，轮换审阅者，降低知识孤岛风险。

**A3. 知识转移训练营**  
针对关键模块组织短期分享或录屏示范，并附练习题，帮助新成员上手。

**A4. 文档健康指标看板**  
统计“过期文档数”“待同步条目数”“审查完成率”等指标，纳入例会跟踪。

**A5. LLM 协作回放**  
记录典型 LLM 协作会话摘要并归档，供后续成员学习最佳实践与常见误区。

**A6. 阅读体验优化**  
为长篇文档提供章节导航或简要摘要，提升阅读效率（保持纯静态实现）。

**A7. 术语学习卡片**  
将高频术语整理为速查卡，附在 `coding_style_guide_for_ai.md` 的附录中。

**A8. 历史洞察专栏**  
在 `new_docs/index.md` 增设“历史洞察”区，记录关键经验、隐含风险与踩坑案例。

**A9. 跨团队分享会**  
定期邀请其他项目成员评审或分享文档改进经验，推动标准复用。

**A10. 文档工具手册**  
扩展 `new_docs/tools_guide.md`，整理编辑、比对、可视化工具的实践技巧，提升执行效率。

**A11. 状态抽样复核**  
在例行审查之外进行随机抽样核查，验证状态标记与内容是否一致，并将结果反馈给对应维护人。

**A12. 词频与冗余检测**  
定期运行简单脚本检测文档中高频或冗余片段，提示作者进行精简，提高可读性。

## 📁 附录：当前文档分类基线

| 文档 | 分类 | 改造备注 |
|------|------|----------|
| `documents/PERFORMANCE_OPTIMIZATION_SUMMARY.md` | guide | 补充 Front Matter 与维护人，加入索引入口 |
| `documents/aimassistant_intro_for_ai.md` | guide | 在 `new_docs/index.md` 建立导航链接 |
| `documents/archive/PERFORMANCE_OPTIMIZATION_JOURNEY.md` | history | 改名为 `performance_optimization_history.md` 后同步引用 |
| `documents/archive/README.md` | reference | 更新描述以反映“history 分类”定位 |
| `documents/archive/aimassistant_implementation_journey.md` | history | 改名为 `aimassistant_implementation_history.md` |
| `documents/archive/autoaim_search_strategy_journey.md` | history | 改名为 `autoaim_search_strategy_history.md` |
| `documents/archive/blocking_delay_implementation_journey.md` | history | 改名为 `blocking_delay_implementation_history.md` |
| `documents/archive/data_collector_integration_journey.md` | history | 改名为 `data_collector_integration_history.md` |
| `documents/archive/gamma_function_refactoring_journey.md` | history | 改名为 `gamma_function_refactoring_history.md` |
| `documents/archive/gimbal_360_implementation_journey.md` | history | 改名为 `gimbal_360_implementation_history.md` |
| `documents/archive/image_preprocessing_complete_journey.md` | history | 改名为 `image_preprocessing_complete_history.md` |
| `documents/archive/preprocessing_troubleshooting_journey.md` | history | 改名为 `preprocessing_troubleshooting_history.md` |
| `documents/archive/recognizer_simplification_journey.md` | history | 改名为 `recognizer_simplification_history.md` |
| `documents/camera_troubleshooting_journey.md` | history | 移入 `documents/history/` 并改名为 `camera_troubleshooting_history.md` |
| `documents/changelog/changelog_2025_10_11.md` | history | 补充 Front Matter 与状态栏 |
| `documents/coding_style_guide_for_ai.md` | reference | 增加术语对照附录与速查卡引用 |
| `documents/development_history_v1.md` | history | 调整分类说明并补齐 Front Matter |
| `documents/development_history_v1_1.md` | history | 调整分类说明并补齐 Front Matter |
| `documents/general_intro_for_ai.md` | guide | 与 `new_docs/index.md` 建立互链 |
| `documents/next_steps.md` | ops | 在索引中标记关键里程碑 |
| `documents/repl.md` | guide | 增加静态流程图并补齐 Front Matter |
| `documents/sdk_protocol_api_document.md` | reference | 标注协议来源与版本 |
| `documents/uart_feedback_decision_journey.md` | history | 改名为 `uart_feedback_decision_history.md` 并更新引用 |
| `documents/utils_module_for_ai.md` | guide | 补充示例与引用路径 |
| `new_docs/problems.md` | ops | 继续记录审查结论与冲突解决 |
| `new_docs/principles.md` | reference | 本文件，按双周节奏复审 |
| `new_docs/zenofpython.md` | culture | 保留理念速查 |

> 调整或新增文档时，必须同步更新本附录与 `new_docs/index.md`，并在 Front Matter 中补齐分类、状态、维护人、更新时间。
