# 项目结构设计方案 ( v1.2 )

## 总览

- `.github/`
    - `copilot-instructions.md` - Copilot 所使用的Prompt

- `model/` - 视觉模型文件
    - `aimbot/` - 自瞄模型
        - `model.pt` - PyTorch 模型文件
        - `model.onnx` - ONNX 模型文件
        - `...` - ncnn, ...

- `tools/` - 工具脚本
    - `repl.py` - 串口通信工具
    - `verify_power.sh` - 树莓派电源检测脚本
    - `set_cpu_performance.sh` - 提升CPU性能脚本
    - `install_cpu_performance_service.sh` - 安装CPU性能服务脚本
    - `uninstall_cpu_performance_service.sh` - 卸载CPU性能服务脚本

- `docs/` - 文档
    - `...`

- `requirements.txt` - Python 依赖列表
- `README.md` - 项目总览文档
- `LICENSE.txt` - GPL-3.0 许可证

## `src/` 目录结构

- `main.py` - **正式比赛**时应该启动的程序
- `logger.py` - 日志工具
- `config.py` - 配置文件 包含 **所有可调参数**
- `vision/` - 视觉相关
    - `camera.py` - 摄像头管理类
    - `...`
- `serial/` - 串口通信相关
    - `conn.py` - 串口连接管理类
    - `dataholder.py` - 串口数据管理类
    - `sdk.py` - 机器人串口模块
    - `blaster.py` - 机器人发射器控制模块
    - `chassis.py` - 机器人底盘控制模块
    - `gimbal.py` - 机器人云台控制模块
    - `robot.py` - 机器人系统控制模块
    - `game_data.py` - 机器人比赛信息模块
- `skill/` - 机器人技能 ___定义___
    - `example.py` - 示例技能模块
    - `aimbot.py` - 自瞄技能模块
    - `...`
- `aimbot/` - 自瞄相关
    - `pipeline.py` - 自瞄处理流水线
    - `selector.py` - 自瞄目标选择模块
    - `...`
