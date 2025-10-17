---
title: RoboMaster EP 明文 SDK 协议速查
version: 2025-10-18
status: active
maintainers:
  - n1ghts4kura
  - GitHub Copilot
category: reference
last_updated: 2025-10-18
related_docs:
  - documents/guide/repl.md
  - documents/history/uart_feedback_decision_history.md
  - documents/guide/utils_module_for_ai.md
llm_prompts:
  - "根据 RoboMaster SDK 协议生成串口命令"
---

# RoboMaster EP 明文 SDK 协议 API 文档

**文档来源**: [RoboMaster 开发者文档](https://robomaster-dev.readthedocs.io/zh-cn/latest/text_sdk/protocol_api.html)  
**整理日期**: 2025年10月4日  
**适用机型**: DJI RoboMaster S1/EP

---

## 📋 文档说明

本文档整理自 DJI 官方 RoboMaster 明文 SDK 协议文档，用于快速查阅串口控制命令。

**命令格式约定**:
- `IN:` 表示发送给机器人的命令
- `OUT:` 表示机器人返回的数据
- 所有命令以分号 `;` 结尾
- 查询指令中的 `?` 与前面命令之间有**一个空格**

---

## 1. SDK 模式控制

### 1.1 进入 SDK 模式
```
IN: command;
```
- **描述**: 控制机器人进入 SDK 模式，进入后才能响应其他控制命令
- **必须**: 主程序启动后首先调用

### 1.2 退出 SDK 模式
```
IN: quit;
```
- **描述**: 退出 SDK 模式，重置所有设置项
- **注意**: Wi-Fi/USB 连接断开时，机器人会自动退出 SDK 模式

---

## 2. 机器人控制

### 2.1 机器人运动模式控制
```
IN: robot mode <mode>
```
- **参数**: 
  - `chassis_lead`: 云台跟随底盘模式（云台 YAW 跟随底盘，云台 YAW 控制失效）
  - `gimbal_lead`: 底盘跟随云台模式（底盘 YAW 跟随云台，底盘 YAW 控制失效）
  - `free`: 自由模式（云台和底盘 YAW 互不影响）
- **示例**: `robot mode chassis_lead;`

### 2.2 机器人运动模式获取
```
IN: robot mode ?;
OUT: <mode>;
```
- **返回值**: `chassis_lead` / `gimbal_lead` / `free`

### 2.3 机器人剩余电量获取
```
IN: robot battery ?;
OUT: <battery_percentage>;
```
- **返回值**: 电量百分比 (int:[1-100])
- **示例**: `OUT: 20;` (剩余电量 20%)

---

## 3. 底盘控制

### 3.1 底盘运动速度控制
```
IN: chassis speed x <speed_x> y <speed_y> z <speed_z>;
```
- **参数**:
  - `speed_x` (float:[-3.5, 3.5]): x 轴速度，单位 m/s
  - `speed_y` (float:[-3.5, 3.5]): y 轴速度，单位 m/s
  - `speed_z` (float:[-600, 600]): z 轴旋转速度，单位 °/s
- **示例**: `chassis speed x 0.1 y 0.1 z 1;`

### 3.2 底盘轮子速度控制
```
IN: chassis wheel w1 <speed_w1> w2 <speed_w2> w3 <speed_w3> w4 <speed_w4>;
```
- **参数**: 各轮速度 (int:[-1000, 1000])，单位 rpm
  - `w1`: 右前麦轮
  - `w2`: 左前麦轮
  - `w3`: 右后麦轮
  - `w4`: 左后麦轮

### 3.3 底盘相对位置控制
```
IN: chassis move { [x <distance_x>] | [y <distance_y>] | [z <degree_z>] } [vxy <speed_xy>] [vz <speed_z>];
```
- **参数**:
  - `distance_x` (float:[-5, 5]): x 轴运动距离，单位 m
  - `distance_y` (float:[-5, 5]): y 轴运动距离，单位 m
  - `degree_z` (int:[-1800, 1800]): z 轴旋转角度，单位 °
  - `speed_xy` (float:(0, 3.5]): xy 轴速度，单位 m/s
  - `speed_z` (float:(0, 600]): z 轴旋转速度，单位 °/s
- **示例**: `chassis move x 0.1 y 0.2;`

### 3.4 底盘速度获取
```
IN: chassis speed ?;
OUT: <x> <y> <z> <w1> <w2> <w3> <w4>;
```
- **返回值**: x/y 速度 (m/s)，z 速度 (°/s)，四轮速度 (rpm)

### 3.5 底盘位置获取
```
IN: chassis position ?;
OUT: <x> <y> <z>;
```
- **返回值**: x 轴位置 (m)，y 轴位置 (m)，偏航角度 (°)

### 3.6 底盘姿态获取
```
IN: chassis attitude ?;
OUT: <pitch> <roll> <yaw>;
```
- **返回值**: pitch/roll/yaw 角度 (°)

### 3.7 底盘状态获取
```
IN: chassis status ?;
OUT: <static> <uphill> <downhill> <on_slope> <pick_up> <slip> <impact_x> <impact_y> <impact_z> <roll_over> <hill_static>;
```
- **返回值**: 11 个状态位 (0/1)
  - `static`: 是否静止
  - `uphill`: 是否上坡
  - `downhill`: 是否下坡
  - `on_slope`: 是否溜坡
  - `pick_up`: 是否被拿起
  - `slip`: 是否滑行
  - `impact_x/y/z`: xyz 轴是否感应到撞击
  - `roll_over`: 是否翻车
  - `hill_static`: 是否在坡上静止

### 3.8 底盘信息推送控制
```
IN: chassis push {[position <switch> pfreq <freq>][attitude <switch> afreq <freq>] | [status <switch> sfreq <switch>] [freq <freq_all>]};
```
- **参数**:
  - `switch`: `on` / `off`
  - `freq`: 推送频率 (int: 1, 5, 10, 20, 30, 50) Hz
- **示例**:
  - `chassis push attitude on;` (打开姿态推送，默认频率)
  - `chassis push position on pfreq 1 attitude on afreq 5;` (分别设置频率)
  - `chassis push freq 10;` (统一设置频率为 10 Hz)

### 3.9 底盘推送信息数据
```
OUT: chassis push <attr> <data>;
```
- **attr** = `position`: `data` = `<x> <y>`
- **attr** = `attitude`: `data` = `<pitch> <roll> <yaw>`
- **attr** = `status`: `data` = `<static> <uphill> ... <hill_static>` (11 个状态位)

---

## 4. 云台控制

### 4.1 云台运动速度控制
```
IN: gimbal speed p <speed> y <speed>;
```
- **参数**:
  - `p` (float:[-450, 450]): pitch 轴速度，单位 °/s
  - `y` (float:[-450, 450]): yaw 轴速度，单位 °/s
- **示例**: `gimbal speed p 1 y 1;`

### 4.2 云台相对位置控制
```
IN: gimbal move { [p <degree>] [y <degree>] } [vp <speed>] [vy <speed>];
```
- **参数**:
  - `p` (float:[-55, 55]): pitch 轴角度，单位 °
  - `y` (float:[-55, 55]): yaw 轴角度，单位 °
  - `vp` (float:[0, 540]): pitch 轴运动速度，单位 °/s
  - `vy` (float:[0, 540]): yaw 轴运动速度，单位 °/s
- **坐标原点**: 当前位置
- **示例**: `gimbal move p 10;`

### 4.3 云台绝对位置控制
```
IN: gimbal moveto { [p <degree>] [y <degree>] } [vp <speed>] [vy <speed>];
```
- **参数**:
  - `p` (int:[-25, 30]): pitch 轴角度 (°)
  - `y` (int:[-250, 250]): yaw 轴角度 (°)
  - `vp` (int:[0, 540]): pitch 轴速度 (°/s)
  - `vy` (int:[0, 540]): yaw 轴速度 (°/s)
- **坐标原点**: 上电位置
- **示例**: `gimbal moveto p 10 y -20 vp 0.1;`

### 4.4 云台休眠控制
```
IN: gimbal suspend;
```
- **描述**: 云台进入休眠，两轴电机释放控制力，不响应任何控制指令
- **警告**: 休眠后需调用 `gimbal resume;` 恢复

### 4.5 云台恢复控制
```
IN: gimbal resume;
```
- **描述**: 从休眠状态恢复

### 4.6 云台回中控制
```
IN: gimbal recenter;
```
- **描述**: 云台回中（回到上电初始位置）

### 4.7 云台姿态获取
```
IN: gimbal attitude ?;
OUT: <pitch> <yaw>;
```
- **返回值**: pitch/yaw 轴角度 (°)
- **示例**: `OUT: -10 20;` (pitch -10°, yaw 20°)

### 4.8 云台信息推送控制
```
IN: gimbal push <attr> <switch> [afreq <freq_all>];
```
- **参数**:
  - `attr`: `attitude`
  - `switch`: `on` / `off`
  - `freq_all`: 推送频率 (Hz)
- **示例**: `gimbal push attitude on;`

### 4.9 云台推送信息数据
```
OUT: gimbal push <attr> <data>;
```
- **attr** = `attitude`: `data` = `<pitch> <yaw>`

---

## 5. 发射器控制

### 5.1 发射器单次发射量控制
```
IN: blaster bead <num>;
```
- **参数**: `num` (int:[1, 5]): 单次发射水弹数量
- **示例**: `blaster bead 2;`

### 5.2 发射器发射控制
```
IN: blaster fire;
```
- **描述**: 发射一次（发射数量由 `blaster bead` 设置）

### 5.3 发射器单次发射量获取
```
IN: blaster bead ?;
OUT: <num>;
```
- **返回值**: 单次发射水弹数
- **示例**: `OUT: 3;`

---

## 6. 装甲板控制

### 6.1 装甲板灵敏度控制
```
IN: armor sensitivity <value>;
```
- **参数**: `value` (int:[1, 10]): 灵敏度，数值越大越容易检测到打击，默认 5

### 6.2 装甲板灵敏度获取
```
IN: armor sensitivity ?;
OUT: <value>;
```

### 6.3 装甲板事件上报控制
```
IN: armor event <attr> <switch>;
```
- **参数**:
  - `attr`: `hit`
  - `switch`: `on` / `off`
- **示例**: `armor event hit on;`

### 6.4 装甲板事件上报数据
```
OUT: armor event hit <index> <type>;
```
- **index** (int:[1, 6]): 装甲板 ID
  - `1` 底盘后
  - `2` 底盘前
  - `3` 底盘左
  - `4` 底盘右
  - `5` 云台左
  - `6` 云台右
- **type** (int:[0, 2]): 攻击类型
  - `0` 水弹攻击
  - `1` 撞击
  - `2` 手敲击
- **示例**: `OUT: armor event hit 1 0;` (1 号装甲板检测到水弹攻击)

---

## 7. 声音识别控制

### 7.1 声音识别事件上报控制
```
IN: sound event <attr> <switch>;
```
- **参数**:
  - `attr`: `applause` (掌声)
  - `switch`: `on` / `off`
- **示例**: `sound event applause on;`

### 7.2 声音识别事件上报数据
```
OUT: sound event <attr> <data>;
```
- **attr** = `applause`: `data` = `<count>` (短时间内击掌次数)
- **示例**: `OUT: sound event applause 2;` (识别到 2 次拍掌)

---

## 8. LED 控制

### 8.1 LED 灯效控制
```
IN: led control comp <comp_str> r <r_value> g <g_value> b <b_value> effect <effect_str>;
```
- **参数**:
  - `comp_str`: LED 编号 (`all` / `top_all` / `top_right` / `top_left` / `bottom_all` / `bottom_front` / `bottom_back` / `bottom_left` / `bottom_right`)
  - `r_value` (int:[0, 255]): RGB 红色分量
  - `g_value` (int:[0, 255]): RGB 绿色分量
  - `b_value` (int:[0, 255]): RGB 蓝色分量
  - `effect_str`: 灯效类型 (`solid` / `off` / `pulse` / `blink` / `scrolling`)
- **示例**: `led control comp all r 255 g 0 b 0 effect solid;` (所有 LED 常亮红色)

---

## 9. 赛事数据获取 (RMYC 专用)

### 9.1 键盘数据推送开启
```
IN: game_msg on;
```
- **描述**: 打开键盘鼠标数据推送

### 9.2 键盘数据推送关闭
```
IN: game_msg off;
```

### 9.3 键盘数据推送数据
```
OUT: game msg push <data>;
```
- **data 格式**: `[cmd_id, len, mouse_press, mouse_x, mouse_y, seq, key_num, key_1, key_2, ...]`
  - `mouse_press`: `1` 右键, `2` 左键, `4` 中键
  - `mouse_x`: 鼠标 x 移动距离 (int:[-100, 100])
  - `mouse_y`: 鼠标 y 移动距离 (int:[-100, 100])
  - `seq`: 序列号 (0-255)
  - `key_num`: 按键数量 (最多 3 个)
  - `key_1, key_2, ...`: 键值 (数字)
- **示例**: `OUT: game msg push [0, 6, 1, 0, 0, 255, 1, 199];`
  - cmd_id=0, len=6, 鼠标右击, 按键 w (199-80=119='w'), 序号 255

---

## 10. 智能识别功能控制

### 10.1 智能识别功能属性控制
```
IN: AI attribute { [line_color <line_color>] [marker_color <marker_color>] [marker_dist <dist>] };
```
- **参数**:
  - `line_color`: `red` / `blue` / `green`
  - `marker_color`: `red` / `blue` / `green`
  - `marker_dist` (float:[0.5, 3]): 视觉标签最小有效距离，单位 m

### 10.2 智能识别功能推送控制
```
IN: AI push <attr> <switch>;
```
- **参数**:
  - `attr`: `person` / `gesture` / `marker` / `line` / `robot`
  - `switch`: `on` / `off`
- **互斥关系**:
  - **A 组**（同时只能开启一个）: `person`, `pose`, `marker`, `robot`
  - **B 组**: `line`
  - 两组间可任意组合
- **示例**: `AI push marker on line on;`

### 10.3 智能识别功能推送数据
```
OUT: AI push <attr> <data>;
```
- **person**: `<n> <x1> <y1> <w1> <h1> ... <xn> <yn> <wn> <hn>`
- **gesture**: `<n> <info1> <x1> <y1> <w1> <h1> ...`
- **marker**: `<n> <info1> <x1> <y1> <w1> <h1> ...`
- **line**: `<n> <x1> <y1> <θ1> <c1> ... <x10n> <y10n> <θ10n> <c10n>` (每条线 10 个点)
- **robot**: `<n> <x1> <y1> <w1> <h1> ...`
- **坐标说明**: x/y/w/h 均为归一化值 [0, 1]，原点在视野左上角
- **示例**: `OUT: AI push person 1 0.5 0.5 0.3 0.7;` (识别到 1 个人，中心点 (0.5, 0.5)，宽 0.3，高 0.7)

---

## 11. 视频流控制

### 11.1 视频流开启控制
```
IN: stream on;
```
- **描述**: 打开视频流，从视频流端口接收 H.264 编码数据

### 11.2 视频流关闭控制
```
IN: stream off;
```

---

## 12. 音频流控制

### 12.1 音频流开启控制
```
IN: audio on;
```
- **描述**: 打开音频流，从音频流端口接收 Opus 编码数据

### 12.2 音频流关闭控制
```
IN: audio off;
```

---

## 13. IP 广播

```
OUT: robot ip <ip_addr>;
```
- **描述**: 未建立连接时，从 IP 广播端口接收到此消息
- **示例**: `OUT: robot ip 192.168.1.102;`

---

## 附录

### A. 常用枚举值

**mode_enum** (机器人运动模式):
- `chassis_lead`: 云台跟随底盘模式
- `gimbal_lead`: 底盘跟随云台模式
- `free`: 自由模式

**switch_enum** (开关):
- `on`: 打开
- `off`: 关闭

**led_effect_enum** (LED 灯效):
- `solid`: 常亮
- `off`: 关闭
- `pulse`: 呼吸
- `blink`: 闪烁
- `scrolling`: 跑马灯

### B. 坐标系说明

**底盘坐标系**:
- x 轴: 正前方
- y 轴: 正左方
- z 轴: 向上旋转为正

**云台坐标系**:
- pitch: 向上抬头为正
- yaw: 向左转为正

### C. 注意事项

1. **查询指令格式**: `?` 前必须有一个空格，如 `chassis speed ?;`
2. **命令结尾**: 所有命令必须以 `;` 结尾
3. **SDK 模式**: 主程序启动后必须先调用 `command;` 进入 SDK 模式
4. **退出清理**: 异常退出时必须调用 `quit;` 释放控制权
5. **运动模式影响**: 
   - 云台跟随底盘模式：云台 YAW 控制失效
   - 底盘跟随云台模式：底盘 YAW 控制失效
6. **云台休眠**: 休眠后两轴电机释放，需调用 `gimbal resume;` 恢复

---

**文档版本**: v1.0  
**最后更新**: 2025年10月4日  
**维护者**: RMYC 项目组
