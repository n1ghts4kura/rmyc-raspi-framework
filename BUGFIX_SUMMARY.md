# Bug 修复总结 (2025-10-10)

## 修复的问题

### 1. set_gimbal_speed(0, 0) 阻塞 Bug
- **症状**: test_serial.py 在 restore_robot_state() 卡住 180 秒
- **根因**: 延时计算错误 360 / max(0, 0, 2) = 180
- **修复**: 速度为 0 时立即返回，不延时
- **文件**: src/bot/gimbal.py

### 2. 云台回中竖直方向失效
- **症状**: 调用 set_gimbal_recenter() 时 pitch 轴不动
- **根因**: 官方 gimbal recenter; 指令不可靠
- **修复**: 使用内部函数 _move_gimbal_absolute(0, 0, 180, 180)
- **文件**: src/bot/gimbal.py

### 3. 连接验证增强
- **需求**: 真正验证下位机连接成功
- **实现**: 自动启动线程 + 发送测试命令 + 验证响应
- **文件**: src/bot/conn.py

## 测试验证

快速测试: python tools/test_fixes.py
完整测试: python tools/test_serial.py

## 相关文档

- documents/blocking_delay_implementation_journey.md
- documents/current_progress.md
