# Copilot Instructions for RMYC Raspi Framework

## 项目架构概览
- 本项目用于在 Raspberry Pi 上控制 RM-S1/EP 机器人，采用 Python 编写。
- 主要模块：
  - `src/bot/`：机器人底层控制（如底盘、云台、发射器、通信等），每个硬件功能有独立模块。
  - `src/aimassitant/`：自瞄与选择器相关逻辑。
  - `src/skill/`：技能系统，支持技能注册、管理与按键绑定。
  - `src/main.py`：主入口，负责整体流程调度。
  - `src/repl.py`：串口交互调试入口。
  - `model/`：存放 AI 模型文件（如 yolov8n.pt）。
  - `documents/`：开发进度、设计说明、AI 辅助总结文档。

## 关键开发流程
- **环境搭建**：
  - 推荐使用虚拟环境：
    ```bash
    python -m venv ./venv
    source ./venv/bin/activate
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 200 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
    ```
- **运行主程序**：
  - 比赛/主流程：`python src/main.py`
  - 串口交互调试：`python src/repl.py`
- **测试**：
  - 测试文件位于项目根目录（如 `test_main.py`、`test_bot.py`）。
  - 直接运行对应测试脚本。

## 项目约定与风格
- **命名规范**：
  - 函数/变量推荐 `[动词]+[名词]`，如 `open_serial()`。
  - 多词组合时优先简单单词叠加。
- **文档维护**：
  - 每次开发前后，AI 需总结进度并写入 `documents/` 下新文档或更新相关文档，命名需清晰反映主题。
  - 避免多个主题混杂于同一文档。
- **模块边界**：
  - 机器人硬件控制与高层技能/自瞄逻辑分离，便于扩展与维护。

## 重要文件/目录
- `src/bot/`：底层硬件控制实现
- `src/aimassitant/`：自瞄与选择器
- `src/skill/`：技能系统
- `src/main.py`、`src/repl.py`：主入口/调试入口
- `documents/`：开发进度与设计文档
- `model/`：AI 模型文件

## 其他说明
- 参考 `README.md` 获取最新开发流程与约定。
- 贡献新模块时，保持与现有结构一致，遵循分层与命名规范。
- 代码提交前，确保相关文档已同步更新。
