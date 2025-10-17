---
title: 自瞄系统实现记录 (Aim Assistant Implementation History)
version: 2025-10-18
status: in-progress
maintainers:
   - n1ghts4kura
   - GitHub Copilot
category: history
last_updated: 2025-10-18
related_docs:
   - documents/history/legacy/aimassistant_intro_for_ai_legacy.md
   - documents/guide/utils_module_for_ai.md
   - documents/guide/PERFORMANCE_OPTIMIZATION_SUMMARY.md
llm_prompts:
   - "追踪自瞄实现过程中的关键决策与待办"
---

# 自瞄系统实现记录 (Aim Assistant Implementation Journey)

**创建日期**: 2025年10月3日  
**作者**: n1ghts4kura  
**阶段**: 初步实现（简化方案 A）

---

## 📋 项目背景

### 需求来源
用户请求实现自瞄（自动瞄准）系统，用于 RMYC 空地协同对抗赛。初期目标是实现基础的自动瞄准功能，后续可扩展卡尔曼滤波等高级特性。

### 硬件环境
- **平台**: Raspberry Pi 4B
- **相机**: gxivision ssp14053838（分辨率 480×320，FOV 待校准）
- **机器人**: DJI RoboMaster S1/EP
- **目标**: 装甲板（135mm × 55mm）

### 技术约束
- 推理速度: 4.15 FPS（已优化）
- 通信方式: UART 串口 (115200 baud)
- 控制延迟: 目标 <250ms

---

## 🤔 关键技术决策

### 决策 1: 测距方案选择

#### 背景问题
AI 提出两种方案：
- **方案 1**: 单目测距（基于相似三角形，需要焦距校准，能得到真实距离）
- **方案 2**: 基于检测框面积的相对优先级（selector.py 已实现，无需校准）

#### 用户反馈
> "我们不需要提前量计算"  
> "根据 selector.py 的逻辑实现更好"

#### 最终决策
**选择方案 2（简化方案 A）**：
- ✅ 只实现角度解算，不实现测距模块
- ✅ 直接使用 `selector_v1()` 选择最优目标
- ✅ 简化流程：检测 → 筛选 → 角度 → 云台控制
- 🔮 后续如需卡尔曼滤波，再添加 `distance.py`

#### 理由
1. 当前阶段无需精确距离（不涉及弹道计算、移动预测）
2. `selector.py` 已通过面积因子隐式表达"远近"优先级
3. 减少校准工作量，快速验证可行性

---

### 决策 2: PID 控制器的取舍

#### 背景问题
原设计文档中包含 PID 控制器，用于平滑云台运动。

#### 用户反馈
> "我们无需使用 PID 控制机器人。直接通过 src/bot 中的模块操控即可。"

#### 最终决策
**移除 PID 控制器**：
- ✅ 直接调用 `bot.gimbal.move_gimbal(pitch, yaw, vpitch, vyaw)`
- ✅ 利用机器人内置的运动控制（已足够平滑）
- ❌ 不实现 `pid.py` 模块

#### 理由
1. RoboMaster SDK 的 `move_gimbal` 已内置速度参数（vpitch/vyaw）
2. 机器人固件层面可能已有 PID 控制
3. 减少代码复杂度，避免重复实现

---

### 决策 3: 配置管理方式

#### 背景问题
参数存储方式：YAML 文件 vs Python 字典。

#### 用户反馈
> "将 yaml 文件的配置写在代码中吧，以字典的形式保存。"

#### 最终决策
**使用 Python 字典**（`config.py`）：
```python
CONFIG = {
    "camera": {"fov": {"horizontal": 70.0, ...}},
    "armor": {"width": 135.0, "height": 55.0},
    ...
}
```

#### 理由
1. 减少外部依赖（无需 PyYAML）
2. 代码即配置，便于版本控制
3. 提供 getter 函数（如 `get_camera_fov()`）封装访问

---

### 决策 4: 相机参数估算

#### 背景问题
无法从公开渠道获取 `gxivision ssp14053838` 的准确规格。

#### 采用方案
使用**典型值估算**，后续校准：
- 水平 FOV: 70° （运动相机常见值）
- 垂直 FOV: 46.7° （按 480:320 比例计算）
- 焦距: 380 像素 （计算值：`(480/2) / tan(70°/2)`）

#### 校准计划
提供工具脚本，让用户通过已知尺寸物体实测校准：
```python
# 未来实现
tools/calibrate_camera_fov.py
```

---

## 💻 实现细节

### 模块架构

#### 已实现模块
1. **config.py** (106 行)
   - 配置字典 `CONFIG`
   - Getter 函数封装（如 `get_camera_fov()`）
   - 支持相机参数、装甲板尺寸、云台控制参数

2. **angle.py** (104 行)
   - `AngleSolver` 类
   - 核心算法：归一化坐标 → 角度
     ```python
     yaw = (xn - 0.5) * fov_h
     pitch = -(yn - 0.5) * fov_v  # 注意负号（图像 y 向下，pitch 向上）
     ```
   - 支持从 `Boxes` 对象或直接坐标计算

3. **pipeline.py** (129 行)
   - `AimAssistantPipeline` 类
   - 主流程：
     ```
     get_latest_boxes() 
       ↓
     selector_v1() 
       ↓
     calculate_angles() 
       ↓
     限制角度范围 
       ↓
     bot.gimbal.move_gimbal()
     ```
   - 包含云台回中、目标信息获取等辅助功能

4. **auto_aim_skill.py** (82 行)
   - 技能函数 `auto_aim_action()`
   - 按键绑定：'z' 键开关自瞄
   - 目标丢失处理：连续 12 帧（~3s）无目标后回中
   - 与现有技能系统无缝集成

#### 未实现模块（暂不需要）
- ❌ `distance.py` - 单目测距
- ❌ `pid.py` - PID 控制器
- ❌ `adaptive.py` - 自适应性能管理

---

### 关键算法

#### 1. 角度解算公式
基于小角度近似和相机 FOV：

```
输入: 归一化坐标 (xn, yn) ∈ [0, 1]
中间量: 相对偏移 dx_norm = xn - 0.5, dy_norm = yn - 0.5
输出:
  yaw = dx_norm × fov_horizontal
  pitch = -dy_norm × fov_vertical  (负号处理坐标系差异)
```

**示例**：
- 目标在图像右上角 (0.8, 0.3)
- dx_norm = 0.3, dy_norm = -0.2
- FOV 70° × 46.7°
- → yaw = 21°, pitch = 9.34°

#### 2. 目标丢失处理
采用计数机制防止频繁回中：

```python
target_lost_count = 0
MAX_LOST_FRAMES = 12  # 约 3 秒

if pipeline.step():
    target_lost_count = 0
else:
    target_lost_count += 1
    if target_lost_count >= MAX_LOST_FRAMES:
        recenter_gimbal()
```

---

### 与现有系统的集成

#### main.py 修改
1. 导入自瞄技能：
   ```python
   from skill.auto_aim_skill import auto_aim_skill
   ```

2. 注册到技能管理器：
   ```python
   skill_manager.add_skill(auto_aim_skill)
   ```

3. 传递 recognizer 实例：
   ```python
   skill_manager.invoke_skill_by_key(
       key, 
       game_msg_dict=ctx.last_game_msg_dict,
       recognizer=recog  # 新增参数
   )
   ```

#### 依赖关系
```
main.py
  ├─ Recognizer (已有)
  ├─ SkillManager (已有)
  └─ auto_aim_skill (新)
       └─ AimAssistantPipeline (新)
            ├─ AngleSolver (新)
            ├─ selector_v1 (已有)
            └─ bot.gimbal (已有)
```

---

## 🐛 遇到的问题与解决

### 问题 1: gimbal.move_gimbal() 参数错误

#### 错误信息
```
参数 "vpitch", "vyaw" 缺少参数
```

#### 原因
初始代码使用了错误的参数名：
```python
gimbal.move_gimbal(
    pitch=pitch,
    yaw=yaw,
    pitch_speed=self.gimbal_speed,  # ❌ 错误
    yaw_speed=self.gimbal_speed     # ❌ 错误
)
```

#### 解决方案
查阅 `bot/gimbal.py` 源码，发现正确参数名：
```python
gimbal.move_gimbal(
    pitch=pitch,
    yaw=yaw,
    vpitch=self.gimbal_speed,  # ✅ 正确
    vyaw=self.gimbal_speed     # ✅ 正确
)
```

---

### 问题 2: BaseSkill 类型错误

#### 错误信息
```
无法访问类"BaseSkill"的属性"set_errored"
```

#### 原因
误以为 `BaseSkill` 有错误处理方法，实际不存在。

#### 解决方案
查阅 `skill/base_skill.py`，发现只需：
- 通过 `return` 提前退出函数
- 使用 `LOG.error()` 记录错误
- `skill.enabled` 状态由框架自动管理

修正代码：
```python
# Before (错误)
skill.set_errored(True)
return

# After (正确)
LOG.error("[AutoAim] 错误信息")
return
```

---

## 📊 参数配置总结

### 当前配置值（config.py）

| 参数类别 | 参数名 | 值 | 状态 | 备注 |
|---------|--------|-----|------|------|
| 相机分辨率 | width | 480 | ✅ 确认 | 已验证 |
| 相机分辨率 | height | 320 | ✅ 确认 | 已验证 |
| 相机 FOV | horizontal | 70.0° | ⚠️ 估算 | 需校准 |
| 相机 FOV | vertical | 46.7° | ⚠️ 估算 | 需校准 |
| 光心 | cx | 240.0 | ✅ 计算 | width/2 |
| 光心 | cy | 160.0 | ✅ 计算 | height/2 |
| 装甲板宽度 | width | 135.0mm | ⚠️ 标准值 | 需实测确认 |
| 装甲板高度 | height | 55.0mm | ⚠️ 标准值 | 需实测确认 |
| 云台速度 | gimbal_speed | 90°/s | ⏳ 待调优 | 需实测调整 |
| 最大偏航角 | max_yaw | 50° | ⏳ 待调优 | 防止超限 |
| 最大俯仰角 | max_pitch | 50° | ⏳ 待调优 | 防止超限 |

### 校准优先级
1. **高优先级**（影响精度）：
   - 相机 FOV（horizontal/vertical）
   - 装甲板实际尺寸

2. **中优先级**（影响体验）：
   - 云台速度 gimbal_speed
   - 角度限制 max_yaw/max_pitch

3. **低优先级**（无需改动）：
   - 光心位置（除非相机畸变严重）

---

## 🧪 测试计划

### 阶段 1: 基础功能验证（树莓派）

**测试步骤**：
1. 运行 `python src/main.py`
2. 按下 'z' 键启动自瞄
3. 观察日志输出：
   ```
   [AimAssistant] 自瞄管线已初始化 | FOV: ...
   [AutoAim] 自瞄已启动，按 'z' 键停止
   [AimAssistant] 瞄准目标 | yaw=XX.XX° pitch=XX.XX°
   ```
4. 检查云台是否朝目标移动
5. 再次按 'z' 停止，确认云台回中

**预期结果**：
- ✅ 无报错
- ✅ 云台能跟随目标移动
- ✅ 频率约 4 次/秒（与推理同步）

---

### 阶段 2: 参数校准

#### 2.1 FOV 校准
使用已知尺寸物体（如 A4 纸）：
1. 将纸张水平放置在摄像头前 1 米处
2. 测量纸张在图像中占据的像素宽度
3. 计算真实 FOV：
   ```
   fov = 2 × arctan(real_width / (2 × distance))
   ```
4. 更新 `config.py` 中的 `CONFIG["camera"]["fov"]`

#### 2.2 云台速度调优
测试不同 `gimbal_speed` 值（30, 60, 90, 120）：
- 过低：响应慢，目标移动时跟不上
- 过高：抖动严重，过冲
- 目标：找到平衡点

---

### 阶段 3: 实战测试

**场景设置**：
- 多个装甲板同时出现
- 目标移动（慢速/快速）
- 不同距离（近/远）

**评估指标**：
1. **选择正确性**：selector 是否选中最优目标（面积最大、离中心最近）
2. **瞄准精度**：云台中心与目标中心的偏差（像素）
3. **响应延迟**：从检测到云台移动的时间（毫秒）
4. **丢失恢复**：目标短暂遮挡后能否快速重新锁定

---

## 🚀 未来扩展方向

### 扩展 1: 单目测距（卡尔曼滤波前置）

**实现时机**：需要预测移动目标时

**实现内容**：
- 创建 `distance.py`
- 实现 `MonocularDistanceEstimator` 类
- 公式：`distance = (real_width × focal_length) / pixel_width`
- 需先校准焦距（通过已知距离物体）

**集成点**：
```python
# pipeline.py 中添加
distance = self.distance_estimator.estimate(target_box)
# 用于卡尔曼滤波初始化
```

---

### 扩展 2: 卡尔曼滤波预测

**实现时机**：目标移动速度快，需要提前量

**实现内容**：
- 创建 `kalman.py`
- 状态向量：`[x, y, z, vx, vy, vz]`（位置 + 速度）
- 观测向量：`[x, y, distance]`（来自检测 + 测距）
- 预测未来 N 帧位置

**关键参数**：
- 过程噪声 Q（目标运动的不确定性）
- 测量噪声 R（检测框 + 测距的误差）

---

### 扩展 3: 自适应性能管理

**实现时机**：需要在精度和速度间动态平衡

**三种模式**：
1. **Fast**: 低精度快速跟踪（适合多目标、快速移动）
2. **Balanced**: 默认模式
3. **Precise**: 高精度慢速瞄准（适合静态目标、狙击）

**切换逻辑**：
```python
if fps < 3 or target_count > 5:
    mode = "fast"
elif target_stable and distance < 2m:
    mode = "precise"
else:
    mode = "balanced"
```

---

### 扩展 4: 多目标优先级策略

**改进点**：
- selector_v1 只考虑面积、中心、置信度
- 未来可加入：
  - 目标颜色（敌我识别）
  - 目标类型（优先攻击哨兵 > 步兵）
  - 威胁等级（正在攻击我方 > 静止目标）

**实现方式**：
```python
# selector.py 中添加新因子
@weight_setting(0.15)
def threat_factor(box, game_state):
    if is_attacking_us(box, game_state):
        return 1.0
    return 0.5
```

---

## 📝 代码规范与最佳实践

### 本次实现遵循的规范

1. **命名约定**：
   - 函数：`[动词]_[名词]`（如 `calculate_angles`）
   - 变量：小写下划线（如 `target_lost_count`）
   - 私有成员：单下划线前缀（暂无）

2. **类型注解**：
   ```python
   def calculate_angles(self, box: Boxes) -> tuple[float, float]:
   ```

3. **文档字符串**：
   - 每个公共函数包含完整 docstring
   - 说明参数范围、返回值、异常

4. **日志规范**：
   ```python
   LOG.debug("[AimAssistant] 调试信息")  # 带模块标识
   LOG.info("[AutoAim] 状态更新")
   LOG.error(f"[AutoAim] 错误: {e}")
   ```

5. **错误处理**：
   - 使用 try-except 包裹硬件调用
   - 避免崩溃，记录日志后优雅降级

---

## ✅ 检查清单

开发完成前确认：

- [x] 所有新文件已创建（config.py, angle.py, pipeline.py, auto_aim_skill.py）
- [x] main.py 已集成自瞄技能
- [x] 类型注解完整
- [x] 日志输出合理
- [x] 文档注释清晰
- [ ] 在树莓派上测试通过（待用户执行）
- [ ] 参数校准完成（待用户执行）
- [ ] 实战效果验证（待用户执行）

---

## 📚 参考资料

- **项目文档**：`documents/general_intro_for_ai.md`
- **自瞄设计**：`documents/aimassistant_intro_for_ai.md`
- **Selector 实现**：`src/aimassistant/selector.py`
- **云台控制 API**：`src/bot/gimbal.py`
- **技能系统**：`src/skill/base_skill.py`, `src/skill/manager.py`

---

## 🔄 版本历史

### v1.0 - 2025年10月3日
- ✅ 初步实现（简化方案 A）
- ✅ 核心模块：config.py, angle.py, pipeline.py
- ✅ 技能集成：auto_aim_skill.py
- ✅ main.py 集成
- ⏳ 待测试：树莓派实机验证

---

**下一步行动**：
1. 用户在树莓派上运行 `python src/main.py`
2. 按 'z' 键测试自瞄功能
3. 根据实际效果调整 `config.py` 参数
4. 反馈问题，迭代优化
