# 🚀 树莓派性能优化快速部署指南

## 📋 优化总览

从 **8 FPS** 提升到 **15+ FPS** 的完整方案。

| 优化项 | 预期提升 | 难度 | 部署时间 |
|--------|---------|------|----------|
| ✅ 智能跳帧 | +100% | ⭐ | 已完成 |
| ✅ 降低分辨率 | +40% | ⭐ | 已完成 |
| ✅ CPU 线程绑定 | +10% | ⭐ | 已完成 |
| ✅ 摄像头硬件加速 | +20% | ⭐ | 已完成 |
| 🔲 系统级优化 | +10% | ⭐⭐ | 5 分钟 |
| 🔲 FP16 模型 | +25% | ⭐⭐ | 10 分钟 |
| 🔲 INT8 量化 | +35% | ⭐⭐⭐⭐ | 1-2 小时 |

**当前基线**: 8 FPS（NCNN FP32）  
**代码优化后**: ~11 FPS（估算）  
**系统优化后**: ~13 FPS  
**FP16 模型**: ~16 FPS ✅ **目标达成！**  
**INT8 量化**: ~20+ FPS 🚀 **终极性能**

---

## 🎯 推荐实施路线

### 路线 A：快速达标（15 FPS）⭐⭐⭐⭐⭐

**耗时**: 30 分钟  
**目标**: 15-16 FPS

```bash
# 步骤 1：上传代码到树莓派（已包含优化）
# 当前 recognizer.py 已优化：
#   - 分辨率降到 320x240
#   - 摄像头硬件加速
#   - CPU 核心绑定
#   - 智能跳帧策略

# 步骤 2：系统级优化（5 分钟）
cd ~/rmyc-raspi-framework
sudo bash tools/optimize_raspberry_pi.sh
# 根据提示完成配置，重启树莓派

# 步骤 3：导出 FP16 模型（10 分钟）
python tools/export_fp16_model.py --size 320
# 导出完成后会提示修改 model_path

# 步骤 4：修改配置使用 FP16 模型
nano src/recognizer.py
# 找到第 90 行左右：
# self.model_path = "./model/yolov8n_ncnn_model"
# 改为：
# self.model_path = "./model/yolov8n_ncnn_fp16"

# 步骤 5：测试性能
python test_annotation.py
# 预期结果：实际推理 FPS 达到 14-16
```

---

### 路线 B：极致性能（20+ FPS）⭐⭐⭐⭐

**耗时**: 2-3 小时  
**目标**: 20-25 FPS

```bash
# 前置条件：完成路线 A

# 步骤 1：采集校准数据（10 分钟）
python << EOF
import cv2
import os

os.makedirs("calibration_data", exist_ok=True)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

print("开始采集 100 张校准图像...")
for i in range(100):
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(f"calibration_data/calib_{i:04d}.jpg", frame)
        if i % 10 == 0:
            print(f"已采集: {i}/100")

cap.release()
print("校准数据采集完成！")
EOF

# 步骤 2：安装 NCNN 工具链（1-2 小时）
cd ~/
git clone https://github.com/Tencent/ncnn.git
cd ncnn
mkdir build && cd build

cmake -DCMAKE_BUILD_TYPE=Release \
      -DNCNN_VULKAN=ON \
      -DNCNN_BUILD_TOOLS=ON \
      ..

make -j4  # 编译需要 1-2 小时
sudo make install

# 步骤 3：INT8 量化（30 分钟）
# 详细步骤见 documents/performance_optimization_guide.md
# 章节：方案 5 - INT8 量化推理

# 步骤 4：测试极致性能
python test_annotation.py
# 预期结果：实际推理 FPS 达到 20-25
```

---

## 🔧 实施细节

### 1. 系统级优化（必做）

```bash
# 一键优化脚本
sudo bash tools/optimize_raspberry_pi.sh
```

**包含以下优化**：
- ✅ GPU 内存 64MB → 256MB
- ✅ CPU 超频 1.5GHz → 1.8GHz
- ✅ GPU 超频 500MHz → 600MHz
- ✅ 禁用蓝牙和不必要服务
- ✅ 设置性能调度器
- ✅ Python 环境变量优化

**重启后验证**：
```bash
check_rpi_perf  # 快速检查性能状态
```

---

### 2. FP16 模型导出（推荐）

```bash
# 导出 320x320 输入的 FP16 模型
python tools/export_fp16_model.py --size 320

# 导出完成后，修改 recognizer.py
nano src/recognizer.py

# 第 90 行左右修改为：
self.model_path = "./model/yolov8n_ncnn_fp16"
```

**预期效果**：
- 推理速度提升 20-30%
- 内存占用减少 50%
- 精度损失 < 1%

---

### 3. 摄像头优化（已集成）

代码已包含以下优化：

```python
# 硬件加速
self.cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)

# MJPEG 格式（减少解码开销）
self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))

# 减少缓冲延迟
self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
```

**无需修改，直接生效**。

---

### 4. CPU 核心绑定（已集成）

代码已自动绑定线程到不同 CPU 核心：

```python
# 采集线程 → CPU 0
os.sched_setaffinity(0, {0})

# 推理线程 → CPU 2-3（性能核心）
os.sched_setaffinity(0, {2, 3})
```

**无需修改，直接生效**。

---

## 📊 性能监控

### 实时监控工具

```bash
# 终端 1：运行程序
python test_annotation.py

# 终端 2：监控系统性能
python tools/monitor_performance.py
```

**监控内容**：
- CPU 频率和温度
- GPU 频率和内存
- 系统内存使用
- 降频/欠压状态
- 性能建议

---

## ⚠️ 常见问题

### Q1: 温度过高（>75°C）

**解决方案**：
1. 加装主动散热风扇
2. 降低超频频率（1800 → 1750 MHz）
3. 改善机箱通风

```bash
# 调整超频频率
sudo nano /boot/config.txt
# 修改 arm_freq=1750  # 降低到 1750
sudo reboot
```

---

### Q2: 系统欠压警告

**解决方案**：
- 更换官方 5V/3A 电源适配器
- 检查 USB 线材质量
- 避免连接过多外设

```bash
# 检查电源状态
vcgencmd get_throttled
# 输出 0x0 表示正常
```

---

### Q3: 推理帧率仍然低于预期

**排查步骤**：

```bash
# 1. 检查系统状态
check_rpi_perf

# 2. 检查模型路径
python -c "
from src.recognizer import Recognizer
r = Recognizer.get_instance()
r.wait_until_initialized()
print(f'Model: {r.model_path}')
print(f'Model loaded: {r.model is not None}')
"

# 3. 检查推理配置
python test_annotation.py
# 查看 "实际推理 FPS" 和 "丢弃帧数"

# 4. 运行基准测试
python << EOF
from ultralytics import YOLO
import time
import numpy as np

model = YOLO("./model/yolov8n_ncnn_fp16")
dummy_img = np.random.randint(0, 255, (320, 240, 3), dtype=np.uint8)

# 预热
for _ in range(5):
    model.predict(dummy_img, verbose=False)

# 基准测试
start = time.time()
for _ in range(50):
    model.predict(dummy_img, verbose=False)
elapsed = time.time() - start

print(f"平均推理时间: {elapsed/50*1000:.2f} ms")
print(f"推理 FPS: {50/elapsed:.2f}")
EOF
```

---

### Q4: 模型精度下降

**解决方案**：

```bash
# 1. 对比不同精度模型的检测结果
python << EOF
from src.recognizer import Recognizer
import cv2

# 测试 FP16 模型
r = Recognizer.get_instance()
r.wait_until_initialized()

# 采集 10 帧进行对比
for i in range(10):
    boxes = r.get_latest_boxes()
    print(f"Frame {i}: {len(boxes)} objects detected")
    time.sleep(0.1)
EOF

# 2. 如果检测数量明显下降，调整置信度阈值
nano src/recognizer.py
# 第 95 行左右：
# self.conf: float = 0.3  # 降低到 0.25 或 0.2
```

---

## 🎯 验收标准

### 性能指标

运行 `python test_annotation.py` 应看到：

```
📊 测试统计
============================================================
总运行时间: 30.0 秒
主循环总帧数: 3000
主循环平均 FPS: 100.00

🔬 推理性能统计
------------------------------------------------------------
推理总帧数: 450              ← 应接近 30 × 15 = 450
丢弃总帧数: 2550            ← 正常现象
目标推理帧率: 15 FPS
实际推理帧率: 14.85 FPS     ← 关键指标，应 ≥ 14
推理效率: 14.75%

🎯 目标检测统计
------------------------------------------------------------
检测到目标的帧数: 380
目标检测率: 84.44%
============================================================
```

**通过标准**：
- ✅ 实际推理帧率 ≥ 14 FPS
- ✅ 目标检测率 > 60%（有目标时）
- ✅ 系统温度 < 75°C
- ✅ 无欠压/降频警告

---

## 📝 部署检查清单

### 代码优化（已完成 ✅）
- [x] 智能跳帧策略
- [x] 降低输入分辨率到 320x240
- [x] 摄像头硬件加速
- [x] CPU 核心绑定
- [x] MJPEG 格式优化
- [x] 减少缓冲区大小

### 系统优化（待执行 🔲）
- [ ] 运行 `sudo bash tools/optimize_raspberry_pi.sh`
- [ ] 重启树莓派
- [ ] 验证超频生效（`check_rpi_perf`）
- [ ] 检查温度 < 75°C

### 模型优化（待执行 🔲）
- [ ] 导出 FP16 模型（`python tools/export_fp16_model.py`）
- [ ] 修改 `recognizer.py` 的 `model_path`
- [ ] 运行测试验证性能

### 最终验收（待执行 🔲）
- [ ] 运行 `test_annotation.py`
- [ ] 实际推理 FPS ≥ 14
- [ ] 温度稳定 < 75°C
- [ ] 无降频警告

---

## 🎉 成功案例预期

**优化前**：
```
[  10s] 推理帧数:    80 | 实际推理FPS:  8.00
```

**优化后**：
```
[  10s] 推理帧数:   150 | 实际推理FPS: 15.20
```

**提升倍率**: 1.9x（90% 提升）🚀

---

## 📚 参考文档

- 完整优化指南：`documents/performance_optimization_guide.md`
- AI 开发指南：`.github/copilot-instructions.md`
- 项目架构：`documents/general_intro_for_ai.md`

---

## 💬 技术支持

如遇到问题，请提供以下信息：

```bash
# 1. 系统状态
check_rpi_perf

# 2. 模型信息
ls -lh model/

# 3. 测试输出
python test_annotation.py 2>&1 | head -50

# 4. 温度历史
vcgencmd measure_temp
```

---

**祝部署顺利！🚀**
