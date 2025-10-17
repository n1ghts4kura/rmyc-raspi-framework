---
title: Utils 工具模块技术摘要
version: 2025-10-18
status: draft
maintainers:
   - n1ghts4kura
   - GitHub Copilot
category: guide
last_updated: 2025-10-18
related_docs:
   - new_docs/principles.md
   - documents/ops/next_steps.md
   - documents/reference/coding_style_guide_for_ai.md
   - src/utils.py
llm_prompts:
   - "总结 utils.py 中的通用图像工具"
---

# 背景与适用范围

- 模块位置：`src/utils.py`，当前仅维护与图像亮度处理相关的公共方法，未来将扩展更多通用工具。
- 适用角色：视觉算法、数据采集、框架维护人员以及协作 AI。
- 当前限制：功能集仍处于早期阶段，因而文档状态设为 `draft`，后续函数上线后需及时补充本文件与中央索引。

## 核心内容

### 模块概览

- 依赖：`cv2`、`numpy`。
- 引用关系：
   - `src/recognizer.py`：在推理前调整亮度。
   - `training/data_collector.py`：采集阶段保持数据一致性。

### 函数详解：`adjust_gamma()`

```python
def adjust_gamma(frame: np.ndarray, gamma: float = 1.0) -> np.ndarray
```

- **用途**：对输入图像执行 Gamma 校正，平衡曝光。
- **参数**：
   - `frame`：BGR 或灰度图像；
   - `gamma`：亮度控制系数，推荐 `0.5 <= gamma <= 2.0`。
- **返回值**：校正后的 `np.ndarray`。
- **算法说明**：
   ```python
   output = (input / 255) ** (1.0 / gamma) * 255
   ```
- **性能特性**：使用 LUT 实现 O(1) 查表，适合实时处理（20 FPS+）。
- **示例**：
   ```python
   from utils import adjust_gamma
   import config

   if config.ENABLE_IMAGE_PREPROCESSING:
         frame = adjust_gamma(frame, config.IMAGE_PREPROCESSING_GAMMA)
   ```

### 版本历史

| 版本 | 日期 | 说明 |
| --- | --- | --- |
| v1.0 | 2025-10-12 | 首次发布 `adjust_gamma()`，完善类型注解与文档字符串 |

### 注意事项

- 训练与推理必须引用相同的 `gamma` 值，推荐统一从 `config.py` 读取。
- 超出建议范围的参数会造成画面失真，应依据场景调优。
- 若新增函数，请同步更新 `__all__` 并编写最小化使用示例。

### 规划中的扩展

- 直方图均衡、CLAHE 包装。
- 色彩空间转换辅助方法。
- 常用降噪（如双边滤波）与锐化操作。
- 后续扩展需补充验证示例与性能评估。

## 操作步骤

1. 在使用方模块中引入：`from utils import adjust_gamma`。
2. 在 `config.py` 中维持统一的 `IMAGE_PREPROCESSING_GAMMA`。
3. 数据采集与推理均调用该函数，确保亮度分布一致。
4. 若调整参数或增加函数，更新 `documents/ops/next_steps.md` 并在 `new_docs/index.md` 记录。

## 验证与状态

- 最近验证：2025-10-12，通过 `training/data_collector.py` 与 `demo_vision.py` 实测。
- 待办：
   - [ ] 评估是否需要新增直方图均衡函数，并补充单元测试。
   - [ ] 在 `new_docs/index.md` 创建索引项，便于快速查找。
   - [ ] 后续扩展完成后将 `status` 更新为 `active`。

## 附录与引用

- 代码引用：`src/utils.py`、`src/recognizer.py`、`training/data_collector.py`
- 相关计划：`documents/ops/next_steps.md`
- 规范依据：`documents/reference/coding_style_guide_for_ai.md`、`new_docs/principles.md`

---
若引入新的工具函数或修改现有接口，请同步更新本文档与中央索引，并在 `new_docs/problems.md` 记录需要评审的风险点。
