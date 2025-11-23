---
slug: uart-communication-journey
title: UART 通信与 SDK 协议演进记录
status: draft
version: v1.1-re
module: bot/conn
created: 2025-11-23
updated: 2025-11-23
llm_summary: >-
  本文用于记录 UART 通信层与 RoboMaster SDK 文本协议封装的演进过程，包括参数选择、可靠性改进和排错经验，目前仅为骨架结构。
---

> 说明：本篇是 **skeleton 文档**，暂时只定义结构，不强行编写详细历史；后续在真实开发过程中再逐步补充内容。

## 1. 背景与设计目标

- 初始通信需求（占位）：
  - 在树莓派与 RoboMaster 之间建立稳定的串口通信链路，支持常见控制与反馈。
- 约束条件（占位）：
  - 仅在树莓派 Linux 上运行，串口设备形如 `/dev/ttyUSB0`。

## 2. 初始实现方案（占位）

- 串口参数选择（波特率、超时等）。
- 与 `docs/reference/sdk_protocol_api_document.md` 中协议的对应关系。

## 3. 关键迭代节点（占位）

- 从“只发命令不看反馈”到“解析反馈并驱动上层逻辑”的过程。
- 针对丢包、乱码、阻塞等问题的应对方案。

## 4. 调试与排错经验（占位）

- REPL 工具在 UART 调试中的使用方式（与 `docs/guide/repl.md` 对应）。
- 常见故障现象与检查顺序。

## 5. 未来规划（占位）

- 是否引入更强的协议封装（心跳、重试等）。
- 与仿真/日志回放工具的潜在配合方式。
