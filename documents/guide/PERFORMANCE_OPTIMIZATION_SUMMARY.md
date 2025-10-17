---
title: 性能优化成果总结
version: 2025-10-17
status: pending-review
maintainers:
  - Copilot Assistant（临时）
category: guide
last_updated: 2025-10-17
related_docs:
  - documents/history/performance_optimization_history.md
  - documents/guide/general_intro_for_ai.md
  - documents/ops/documentation_issues.md
source_code_paths:
  - src/recognizer.py
  - src/skill/autoaim.py
  - tools/test_fixes.py
---

# 性能优化成果总结

> **适用角色**：性能调优工程师、视觉算法开发、协作 AI。
>
> **前置要求**：熟悉树莓派环境、能够运行 `tools/test_fixes.py`、了解 `config.py` 中的性能相关参数。

## 背景与适用范围

- 目标：解决 v1.0 阶段存在的推理帧率低、CPU 降频、串口线程饥饿等问题，使自瞄链路达到比赛可用水平。
- 硬件环境：Raspberry Pi 4B + 官方 5V/3A 电源 + YOLOv8n ONNX。
- 时间范围：2025-09-20 ~ 2025-10-02，详见 `documents/history/performance_optimization_history.md`。

## 核心内容

### 优化前后对比

| 指标 | 优化前 | 优化后 | 提升 |
| --- | --- | --- | --- |
| 主循环 FPS | 3.82 | 10,192 | ↑ 2,667x |
| 主循环单次耗时 | 277ms | 0.093ms | ↑ 2,978x |
| 推理时间 | 920ms | 204ms | ↑ 4.5x |
| 推理 FPS | 1.09 | 4.89 | ↑ 4.5x |
| 推理时间标准差 | ±153ms | ±3.9ms | 稳定性提升 39x |

### 核心优化措施

1. **移除 `time.sleep()` 瓶颈**：主循环与推理线程均改为非阻塞轮询，避免调度器延迟。
2. **智能休眠调度**：当推理线程未更新时，主循环短暂休眠 10ms，避免 CPU 饥饿。
3. **升级电源**：更换为 5V/3A 官方电源，CPU 维持 1800MHz 满频运行。
4. **推理后端切换**：由 NCNN Vulkan 改为 ONNX Runtime CPU，消除崩溃并提升稳定性。
5. **输入分辨率校准**：统一采用 480×320，兼顾精度与速度。

### 可用性评估

| 指标 | 目标 | 实测 | 结论 |
| --- | --- | --- | --- |
| 推理时间 | < 250ms | 204ms | ✅ 达标 |
| 推理 FPS | > 4 | 4.89 | ✅ 达标 |
| 主循环实时性 | ≥ 90 FPS | 10,192 FPS | ✅ 余量充足 |
| CPU 温度 | < 70°C | 52–56°C | ✅ 安全 |
| 长时间运行 | 无崩溃 | 30min 稳定 | ✅ 可靠 |

## 操作步骤

1. **环境准备**：
   - 安装 ONNX Runtime（`pip install onnxruntime`）。
   - 检查电源为 5V/3A 官方电源，确认 `vcgencmd get_throttled` 输出为 `0x0`。
2. **代码同步**：
   - 确保 `recognizer.py` 使用非阻塞队列轮询。
   - 在 `skill/autoaim.py` 启用智能休眠逻辑。
3. **验证流程**：
   - 运行 `tools/test_fixes.py --profile` 获取主循环与推理耗时。
   - 使用 `Recognizer.get_fps_info()` 验证推理帧率与波动范围。
   - 记录核心指标并更新 `documents/ops/documentation_issues.md`。

## 验证与状态

- 当前状态：`pending-review`，等待硬件实战测试结果。
- 验证结果：
  - 主循环与推理链路均满足实时性要求。
  - 长时间运行无欠压与崩溃，CPU 温度保持 52°C 左右。
- 风险提示：
  - 更换摄像头或模型后需重新评估。
  - 若电源不足（<2A），CPU 会降频导致性能回退。
- 尚缺数据点：图像预处理上线后的帧率与延迟对比未在仓库文档中记录，需在完成功能验证后补充至 `documents/history/performance_optimization_history.md` 或新增条目。

## 附录与引用

- 历史记录：`documents/history/performance_optimization_history.md`
- 操作指南：`documents/guide/repl.md`
- 问题追踪：`documents/ops/documentation_issues.md`
- 相关脚本：`tools/test_fixes.py`、`tools/install_cpu_performance_service.sh`

---
后续若进行模型量化或分辨率调整，请更新本指南的对比表，并在提交信息中注明所遵循的原则编号（例如 M1、M10）。
