# 相机 FOV 配置改进记录

## 改进时间
2025年10月3日

## 问题背景

用户提出疑问：**"相机的 FOV 没有遇到过分横纵向谈的"**

这是一个非常**正确且重要的工程实践观察**！

## 原始配置的问题

### 配置方式（不符合工程实践）
```python
# 原配置：手动分别设置水平和垂直 FOV
CAMERA_FOV_HORIZONTAL = 70.0°
CAMERA_FOV_VERTICAL = 46.7°   # 这个值从哪来？需要单独校准吗？
```

### 存在的问题
1. **不符合相机规格表习惯**：大部分相机厂商只标注一个 FOV 值（对角线或水平）
2. **引入冗余参数**：垂直 FOV 实际上可以从水平 FOV 和传感器长宽比计算得出
3. **增加校准复杂度**：需要分别测量两个 FOV，容易出错
4. **理论不自洽**：当前配置的 46.7° 与理论计算的 50.05° 有 3.35° 偏差

## 针孔相机模型的数学关系

### 基本原理
对于理想的针孔相机，水平 FOV 和垂直 FOV 由传感器的**物理尺寸比例**决定：

```
tan(FOV_V / 2)     height
───────────────  = ──────
tan(FOV_H / 2)     width
```

### 推导公式
```python
FOV_V = 2 × arctan(tan(FOV_H / 2) × height / width)
```

### 验证计算
以当前配置为例：
```python
CAMERA_WIDTH = 480
CAMERA_HEIGHT = 320
aspect_ratio = 320 / 480 = 0.6667  # 约 2:3

FOV_H = 70.0°
FOV_V_calculated = 2 × arctan(tan(70°/2) × 0.6667) = 50.05°

# 与原配置的偏差
偏差 = |50.05° - 46.7°| = 3.35°
```

## 改进方案

### 新配置方式
```python
# 只配置水平 FOV（符合相机规格表习惯）
CAMERA_FOV_HORIZONTAL = 70.0°  # 从相机规格表获取或实测

# 垂直 FOV 在代码中自动计算（无需配置）
```

### 实现代码（`angle.py`）
```python
import math
import config

def calculate_angles(box: Boxes) -> tuple[float, float]:
    # 根据针孔相机模型自动计算垂直 FOV
    fov_h_rad = math.radians(config.CAMERA_FOV_HORIZONTAL)
    aspect_ratio = config.CAMERA_HEIGHT / config.CAMERA_WIDTH
    fov_v_rad = 2 * math.atan(math.tan(fov_h_rad / 2) * aspect_ratio)
    fov_v_deg = math.degrees(fov_v_rad)
    
    # 使用计算得到的垂直 FOV
    yaw = dx_norm * config.CAMERA_FOV_HORIZONTAL
    pitch = -dy_norm * fov_v_deg
    
    return yaw, pitch
```

## 优势对比

| 方面 | 原方案（两个 FOV） | 新方案（一个 FOV） |
|------|-------------------|-------------------|
| **符合工程实践** | ❌ 不符合（相机规格表很少同时标注） | ✅ 符合（只需查阅水平 FOV） |
| **参数数量** | 2 个独立参数 | 1 个参数 + 自动推导 |
| **校准复杂度** | 需分别测量 H 和 V | 只需测量 H |
| **理论一致性** | ❌ 可能不满足几何关系 | ✅ 严格满足针孔相机模型 |
| **适应性** | 修改分辨率需重新校准两个值 | 修改分辨率自动适配 |

## 实测数据对比

### 计算结果
```
图像分辨率: 480 × 320 (3:2)
水平 FOV: 70.0°
垂直 FOV (自动计算): 50.05°
原配置垂直 FOV: 46.7°
偏差: 3.35°
```

### 不同位置的角度计算示例
| 目标位置 | 归一化坐标 | Yaw (°) | Pitch (°) |
|---------|-----------|---------|-----------|
| 图像中心 | (0.5, 0.5) | 0.00 | 0.00 |
| 右上角 | (1.0, 0.0) | +35.00 | +25.02 |
| 左下角 | (0.0, 1.0) | -35.00 | -25.02 |
| 右上方偏中 | (0.8, 0.3) | +21.00 | +10.01 |

## 常见相机 FOV 参考

| 相机类型 | 典型水平 FOV | 垂直 FOV (4:3) | 垂直 FOV (16:9) |
|---------|-------------|---------------|----------------|
| 树莓派 Camera V2 | 62.2° | 48.8° | 41.4° |
| 罗技 C920 | 70.4° | 55.0° | 43.3° |
| GoPro Hero 9 | 118° (Wide) | 98.0° | 69.5° |
| 手机前置摄像头 | 60-80° | 47-62° | 39-50° |

## 实际应用建议

### 1. 获取水平 FOV 的方法

#### 方法 A：查阅相机规格表（推荐）
- 查找官方文档或产品页面
- 关键词：`Field of View`, `FOV`, `Viewing Angle`
- 注意区分对角线 FOV 和水平 FOV

#### 方法 B：实测校准
```python
# 步骤：
1. 放置已知宽度的标定板（如 A4 纸宽度 = 210mm）
2. 调整距离，使标定板刚好占满图像宽度
3. 测量相机到标定板的距离 d
4. 计算 FOV_H = 2 × arctan(宽度 / (2 × d))

# 示例：
标定板宽度 = 210mm
距离 d = 150mm
FOV_H = 2 × arctan(210 / (2 × 150)) = 2 × arctan(0.7) = 70.0°
```

### 2. 特殊情况处理

#### 畸变镜头（广角/鱼眼）
- 针孔相机模型不再适用
- 需要使用镜头畸变校正
- 建议使用 OpenCV 的 `cv2.undistort()`

#### 变焦镜头
- FOV 会随变焦变化
- 需要固定焦距或动态更新 FOV
- 考虑使用焦距参数代替 FOV

## 后续优化方向

### 短期
- ✅ 已完成：使用单一水平 FOV + 自动计算
- ⏳ 待完成：实测校准实际相机的水平 FOV

### 中期
- 添加镜头畸变校正（如果使用广角镜头）
- 支持配置文件中指定对角线 FOV（自动转换为水平 FOV）

### 长期
- 实现基于棋盘格标定的完整相机内参标定
- 支持多种镜头模型（针孔/广角/鱼眼）

## 相关文件修改

### 修改的文件
1. **`src/config.py`**
   - 删除 `CAMERA_FOV_VERTICAL` 配置项
   - 保留 `CAMERA_FOV_HORIZONTAL`（添加详细注释）

2. **`src/aimassistant/angle.py`**
   - 添加 `import math`
   - 在 `calculate_angles()` 中自动计算垂直 FOV
   - 更新文档字符串

3. **`test_fov_calculation.py`** (新增)
   - 验证 FOV 计算正确性的测试脚本

### 验证结果
```bash
✅ config.py 编译通过
✅ angle.py 编译通过
✅ FOV 计算验证通过（偏差 3.35°）
```

## 参考资料

1. **针孔相机模型**
   - OpenCV 相机标定文档：https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
   
2. **FOV 计算器**
   - https://www.scantips.com/lights/fieldofview.html
   
3. **常见相机规格**
   - Raspberry Pi Camera: https://www.raspberrypi.com/documentation/accessories/camera.html
   - Logitech C920: https://www.logitech.com/en-us/products/webcams/c920-pro-hd-webcam.html

## 总结

用户的质疑**完全正确**！相机 FOV 确实不应该分横纵向单独配置。通过改为**单一水平 FOV + 自动计算**的方案：

1. ✅ 符合工程实践（相机规格表习惯）
2. ✅ 减少配置参数（从 2 个减少到 1 个）
3. ✅ 保证理论一致性（严格满足针孔相机模型）
4. ✅ 简化校准流程（只需测量一个值）
5. ✅ 提升适应性（修改分辨率自动适配）

这是一次**非常有价值的工程优化**！🎉
