---
title: 预处理阶段下一步行动清单
version: 2025-10-18
status: active
maintainers:
  - n1ghts4kura
  - GitHub Copilot
category: ops
last_updated: 2025-10-18
related_docs:
    - new_docs/principles.md
    - documents/history/release_2025_10_11_history.md
    - documents/guide/utils_module_for_ai.md
    - documents/reference/coding_style_guide_for_ai.md
llm_prompts:
  - "规划预处理阶段的执行优先级"
---

# 背景与适用范围

- 本文驱动图像预处理链路在 v1.1 阶段的落地，从验证到数据采集、训练与集成测试均在此跟踪。
- 适用团队角色：算法、数据采集、运维、协作 AI。
- 参考状态：图像预处理方案已设计完成（见 `documents/history/release_2025_10_11_history.md`），需要按计划完成实施与验证。

## 核心内容

### 任务分层概览

| 时间范围 | 任务 | 负责人 | 状态 |
| --- | --- | --- | --- |
| 即日 | 验证预处理功能 | 待指派 | 进行中 |
| 1-3 天 | 多场景数据采集 | 待指派 | 未开始 |
| 3-7 天 | 参数调优、YOLO 训练 | 待指派 | 未开始 |
| 1-2 周 | 系统集成测试、性能复核 | 待指派 | 未开始 |

### 关键约束

- 修改 `IMAGE_PREPROCESSING_GAMMA` 时必须重新采集数据。
- 训练与推理的预处理流程保持一致，全部参数由 `config.py` 管理。
- 若依赖文档缺失（例如 `documents/task_completion_summary.md`），需要创建占位并在中央索引登记。

## 操作步骤

### 即日行动（高优先级）

1. **验证数据采集链路**
    ```bash
    python training/data_collector.py
    ```
    - [ ] 预览图像亮度符合 `gamma=1.3` 预期。
    - [ ] 按 `c` 保存的图片已应用预处理。
    - [ ] 按 `v` 录制的视频帧包含预处理效果。
    - [ ] 确认输出目录 `training/photos/` 与 `training/videos/` 中数据可用。

2. **验证实时预测链路**
    ```bash
    python demo_vision.py
    ```
    - [ ] 终端日志提示预处理启用。
    - [ ] 实际检测结果较未开启预处理时有显著改善。

### 短期任务（1-3 天）

1. **多场景数据采集计划**
    | 场景 | 光照 | 目标数量 | 优先级 |
    | --- | --- | --- | --- |
    | 正常光照 | 室内均匀光源 | ≥200 张 | 高 |
    | 强光 | 靠窗或室外 | ≥100 张 | 中 |
    | 弱光 | 阴影/昏暗 | ≥100 张 | 中 |
    | 混合光 | 多光源干扰 | ≥50 张 | 低 |
    - 数据质量要求：目标清晰、多角度、多距离、包含干扰物。

2. **采集流程指引**
    ```bash
    python training/data_collector.py  # 启动采集
    ```
    - 按 `+`/`-` 调整焦距；`c` 拍照；`v` 开始/停止录像；`q` 退出。
    - 数据存储路径：`training/photos/`、`training/videos/`。

### 中期任务（3-7 天）

1. **参数调优**
    ```bash
    vim src/config.py  # 调整 IMAGE_PREPROCESSING_GAMMA
    python training/data_collector.py  # 重新采集
    python demo_vision.py  # 验证效果
    ```
    - 建议：
      - 过亮场景可降至 `0.9`；
      - 正常场景保留 `1.3`；
      - 过暗场景可升至 `1.8`。

2. **YOLO 模型训练准备**
    ```bash
    from ultralytics import YOLO
    model = YOLO('yolov8n.pt')
    model.train(data='path/to/data.yaml', epochs=100, imgsz=640, batch=16, device='cpu')
    ```
    - 先完成标注、划分训练/验证/测试集（7:2:1）。

### 长期任务（1-2 周）

1. **系统集成测试**
    ```bash
    python src/main.py
    ```
    - 验证技能触发、串口通信、硬件响应。
    - 监控 FPS、CPU、内存。

2. **性能优化备选项**
    - [ ] 探索更轻量模型（如 YOLOv8n-lite）。
    - [ ] 调整分辨率（640×480 → 480×320）。
    - [ ] 线程解耦视觉、控制、通信。

## 验证与状态

- 当前状态为 `active`，最近一次更新时间 2025-10-18。
- 需要建立验证记录，建议在完成每个阶段后于 `new_docs/problems.md` 或中央索引中登记结论。
- 缺失文档：`documents/task_completion_summary.md`、`documents/checklist_image_preprocessing.md`、`documents/image_preprocessing_implementation.md` 暂未在仓库中找到，需在执行前补建或调整引用。

## 附录与引用

- 相关文件：`src/config.py`、`training/data_collector.py`、`demo_vision.py`
- 参考文档：`documents/guide/utils_module_for_ai.md`、`documents/reference/coding_style_guide_for_ai.md`
- 规范依据：`new_docs/principles.md`

---
完成任一任务后，请在 24 小时内更新中央索引与本计划，并在 `new_docs/problems.md` 记录遇到的风险或阻塞项。
