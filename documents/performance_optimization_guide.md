# 树莓派 4B YOLO 推理性能优化完整指南

## 📊 当前性能基线
- **硬件**: Raspberry Pi 4B 4GB
- **模型**: YOLOv8n NCNN
- **当前帧率**: 8 FPS
- **目标帧率**: 15+ FPS

---

## 🚀 优化方案（按效果排序）

### 方案 1: 启用 Raspberry Pi GPU 加速（VideoCore VI）⭐⭐⭐⭐⭐
**预期提升**: 30-50%（8 FPS → 10-12 FPS）
**难度**: 中等

#### 原理
树莓派 4B 内置 VideoCore VI GPU，支持硬件加速的图像预处理（缩放、色彩转换）和部分 NN 操作。

#### 实现步骤

##### 1.1 安装 OpenGL ES 支持
```bash
sudo apt-get update
sudo apt-get install -y \
    libgles2-mesa-dev \
    libgbm-dev \
    libdrm-dev \
    python3-opengl
```

##### 1.2 启用 GPU 内存分配（关键！）
```bash
# 编辑 /boot/config.txt
sudo nano /boot/config.txt

# 添加以下行（分配更多 GPU 内存）
gpu_mem=256  # 默认 64MB，提升到 256MB

# 重启生效
sudo reboot
```

##### 1.3 启用 VideoCore 硬件加速
```python
# 在 _init_camera() 中添加
def _init_camera(self) -> bool:
    self.cap = cv2.VideoCapture(0)
    if not self.cap.isOpened():
        return False
    
    # 🔥 启用硬件加速后端
    self.cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
    
    # 优化缓冲区设置
    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减少缓冲延迟
    
    # 设置分辨率和帧率
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)
    self.cap.set(cv2.CAP_PROP_FPS, self.cam_fps)
    
    # 🔥 使用 MJPEG 格式减少解码开销
    self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
    
    return True
```

##### 1.4 OpenCV GPU 模块编译（进阶）
如果需要更强的 GPU 加速，可以编译带 OpenGL 支持的 OpenCV：

```bash
# 安装依赖
sudo apt-get install -y build-essential cmake git \
    libgtk-3-dev libavcodec-dev libavformat-dev \
    libswscale-dev libv4l-dev libxvidcore-dev \
    libx264-dev libjpeg-dev libpng-dev libtiff-dev \
    gfortran openexr libatlas-base-dev \
    libtbb2 libtbb-dev libdc1394-22-dev

# 克隆 OpenCV（4.8.0 稳定版）
cd ~/
git clone --depth 1 --branch 4.8.0 https://github.com/opencv/opencv.git
cd opencv
mkdir build && cd build

# 配置编译参数（启用 OpenGL）
cmake -D CMAKE_BUILD_TYPE=RELEASE \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D WITH_OPENGL=ON \
      -D WITH_V4L=ON \
      -D WITH_TBB=ON \
      -D BUILD_TESTS=OFF \
      -D BUILD_PERF_TESTS=OFF \
      -D BUILD_EXAMPLES=OFF \
      ..

# 编译（耗时约 2-3 小时）
make -j4
sudo make install
```

---

### 方案 2: 优化 NCNN 推理参数⭐⭐⭐⭐⭐
**预期提升**: 20-30%（8 FPS → 9.6-10.4 FPS）
**难度**: 简单

#### 2.1 使用 Vulkan GPU 加速（树莓派 4B 支持）
```python
def _init_model(self) -> bool:
    """初始化 YOLO 模型，启用 NCNN Vulkan 加速"""
    try:
        # 🔥 关键：task='detect' 明确任务类型，减少初始化开销
        self.model = YOLO(self.model_path, task='detect')
        
        # 如果是 NCNN 模型，可以通过 ultralytics 的参数传递
        # 注意：需要检查 Ultralytics 版本是否支持 NCNN Vulkan
        
        logger.info(f"YOLO 模型加载完成: {self.model_path}")
        return True
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        return False
```

#### 2.2 手动启用 NCNN Vulkan（如果 Ultralytics 不支持）
创建自定义推理脚本 `src/ncnn_predictor.py`:

```python
"""
自定义 NCNN 推理器，直接使用 pyncnn 获得最佳性能
"""
import ncnn
import cv2
import numpy as np

class NCNNPredictor:
    def __init__(self, param_path: str, bin_path: str, 
                 input_size: int = 320, use_gpu: bool = True):
        """
        Args:
            param_path: .param 文件路径
            bin_path: .bin 文件路径
            input_size: 输入尺寸（320/416/640）
            use_gpu: 是否使用 Vulkan GPU 加速
        """
        self.net = ncnn.Net()
        
        # 🔥 启用 Vulkan GPU
        if use_gpu:
            self.net.opt.use_vulkan_compute = True
        
        # 性能优化选项
        self.net.opt.use_fp16_arithmetic = True  # FP16 运算
        self.net.opt.use_fp16_storage = True     # FP16 存储
        self.net.opt.num_threads = 4             # 4 核 CPU
        
        # 加载模型
        self.net.load_param(param_path)
        self.net.load_model(bin_path)
        
        self.input_size = input_size
    
    def preprocess(self, img: np.ndarray) -> ncnn.Mat:
        """图像预处理"""
        # 缩放到模型输入尺寸
        img_resized = cv2.resize(img, (self.input_size, self.input_size))
        
        # BGR to RGB
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        
        # 归一化到 [0, 1]
        img_norm = img_rgb.astype(np.float32) / 255.0
        
        # 转换为 NCNN Mat
        mat = ncnn.Mat.from_pixels(
            img_rgb, 
            ncnn.Mat.PixelType.PIXEL_RGB,
            self.input_size, 
            self.input_size
        )
        
        # 归一化
        mean_vals = [0.0, 0.0, 0.0]
        norm_vals = [1/255.0, 1/255.0, 1/255.0]
        mat.substract_mean_normalize(mean_vals, norm_vals)
        
        return mat
    
    def predict(self, img: np.ndarray, conf_thresh: float = 0.3):
        """
        执行推理
        
        Returns:
            List[List[float]]: [[x1, y1, x2, y2, conf, cls], ...]
        """
        mat_in = self.preprocess(img)
        
        # 创建 Extractor
        ex = self.net.create_extractor()
        ex.input("images", mat_in)  # 输入层名称，根据模型调整
        
        # 推理
        ret, mat_out = ex.extract("output0")  # 输出层名称，根据模型调整
        
        # 后处理（简化版，实际需要 NMS）
        boxes = self._postprocess(mat_out, conf_thresh, img.shape)
        
        return boxes
    
    def _postprocess(self, mat_out, conf_thresh, orig_shape):
        """后处理：过滤低置信度框 + NMS"""
        # 这里需要根据 YOLOv8 的输出格式实现
        # 简化示例，实际需要完整的解码逻辑
        boxes = []
        # ... 解码逻辑 ...
        return boxes
```

#### 2.3 在 recognizer.py 中集成
```python
# 修改 _init_model()
def _init_model(self) -> bool:
    try:
        # 使用自定义 NCNN 推理器
        param_path = "./model/yolov8n_ncnn_model/model.ncnn.param"
        bin_path = "./model/yolov8n_ncnn_model/model.ncnn.bin"
        
        self.predictor = NCNNPredictor(
            param_path=param_path,
            bin_path=bin_path,
            input_size=320,  # 降低分辨率提速
            use_gpu=True     # 启用 Vulkan
        )
        logger.info("NCNN 推理器初始化完成（Vulkan GPU）")
        return True
    except Exception as e:
        logger.error(f"NCNN 推理器初始化失败: {e}")
        return False

# 修改 _process_frame()
def _process_frame(self, frame):
    if self.predictor is None:
        return
    
    try:
        # 使用自定义推理器
        boxes = self.predictor.predict(frame, conf_thresh=self.conf)
        
        with self._lock:
            self._latest_boxes = boxes
        
        self._predict_frame_count += 1
    except Exception as e:
        logger.error(f"推理失败: {e}")
```

---

### 方案 3: 降低输入分辨率⭐⭐⭐⭐⭐
**预期提升**: 40-60%（8 FPS → 11.2-12.8 FPS）
**难度**: 极简单

#### 原理
推理时间与输入像素数成平方关系：`Time ∝ (Width × Height)²`

#### 实现
```python
class Recognizer:
    def __init__(
        self,
        cam_width: int = 320,      # 从 480 降到 320
        cam_height: int = 240,     # 从 320 降到 240
        imshow_width: int = 160,
        imshow_height: int = 120,
        cam_fps: float = 60.0,
        inference_fps: int = 15,
        model_input_size: int = 256,  # 🆕 YOLO 输入尺寸（256/320/416）
    ):
        self.model_input_size = model_input_size
        # ... 其他参数 ...
```

#### YOLO 输入尺寸对比
| 尺寸 | 像素数 | 相对速度 | 检测精度 | 推荐场景 |
|------|--------|----------|----------|----------|
| 640×640 | 409K | 1.0× | ★★★★★ | 高精度需求 |
| 416×416 | 173K | 2.4× | ★★★★☆ | 平衡 |
| 320×320 | 102K | 4.0× | ★★★☆☆ | 实时性优先 |
| 256×256 | 65K | 6.3× | ★★★☆☆ | 极致速度 |

**建议**: 使用 320×320 或 256×256，在 RoboMaster 场景下精度足够。

---

### 方案 4: FP16 半精度推理⭐⭐⭐⭐
**预期提升**: 15-25%（8 FPS → 9.2-10 FPS）
**难度**: 简单

#### 4.1 重新导出 NCNN 模型（FP16）
```bash
# 在树莓派上执行
cd ~/rmyc-raspi-framework

# 使用 Ultralytics 导出 FP16 模型
python3 << EOF
from ultralytics import YOLO

# 加载原始 PyTorch 模型
model = YOLO("model/yolov8n.pt")

# 导出为 NCNN (FP16)
model.export(
    format="ncnn",
    half=True,  # 🔥 关键：启用 FP16
    imgsz=320,  # 输入尺寸
    simplify=True
)
EOF

# 导出的模型在 model/yolov8n_ncnn_model/
```

#### 4.2 验证 FP16 模型
```bash
# 检查 .param 文件中是否包含 fp16 标记
grep -i "fp16" model/yolov8n_ncnn_model/model.ncnn.param
```

#### 4.3 修改加载逻辑
```python
def _init_model(self) -> bool:
    self.model_path = "./model/yolov8n_ncnn_model"  # FP16 版本
    
    try:
        self.model = YOLO(self.model_path, task='detect')
        
        # 如果使用自定义 NCNN 推理器
        # self.net.opt.use_fp16_arithmetic = True
        # self.net.opt.use_fp16_storage = True
        
        logger.info(f"FP16 模型加载完成")
        return True
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        return False
```

---

### 方案 5: INT8 量化推理（高级）⭐⭐⭐⭐
**预期提升**: 30-50%（8 FPS → 10.4-12 FPS）
**难度**: 困难

#### 原理
INT8 量化将模型权重和激活从 32 位浮点数压缩到 8 位整数，内存占用减少 4 倍，计算速度提升 2-4 倍。

#### 5.1 准备校准数据集
```python
# calibration_dataset.py
import cv2
import os
from pathlib import Path

def prepare_calibration_data(output_dir: str = "./calibration_data", num_images: int = 100):
    """从摄像头采集校准数据"""
    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    
    print(f"采集 {num_images} 张校准图像...")
    count = 0
    
    while count < num_images:
        ret, frame = cap.read()
        if ret:
            save_path = os.path.join(output_dir, f"calib_{count:04d}.jpg")
            cv2.imwrite(save_path, frame)
            count += 1
            
            if count % 10 == 0:
                print(f"已采集: {count}/{num_images}")
        
    cap.release()
    print("校准数据采集完成！")

if __name__ == "__main__":
    prepare_calibration_data()
```

#### 5.2 导出 INT8 量化模型
```python
# export_int8_model.py
from ultralytics import YOLO
from pathlib import Path

def export_int8_ncnn():
    # 加载模型
    model = YOLO("model/yolov8n.pt")
    
    # 导出为 ONNX（中间格式）
    onnx_path = model.export(
        format="onnx",
        imgsz=320,
        simplify=True
    )
    
    print(f"ONNX 模型已导出: {onnx_path}")
    
    # 使用 NCNN 工具进行 INT8 量化
    # 需要在树莓派上安装 ncnn-tools
    import subprocess
    
    subprocess.run([
        "onnx2ncnn",
        onnx_path,
        "model/yolov8n_int8.param",
        "model/yolov8n_int8.bin"
    ])
    
    # INT8 量化（需要校准数据）
    subprocess.run([
        "ncnnoptimize",
        "model/yolov8n_int8.param",
        "model/yolov8n_int8.bin",
        "model/yolov8n_int8_opt.param",
        "model/yolov8n_int8_opt.bin",
        "65536"  # INT8 量化标志
    ])

if __name__ == "__main__":
    export_int8_ncnn()
```

#### 5.3 安装 NCNN 工具（树莓派）
```bash
# 安装依赖
sudo apt-get install -y build-essential git cmake \
    libprotobuf-dev protobuf-compiler \
    libopencv-dev

# 克隆 NCNN
cd ~/
git clone https://github.com/Tencent/ncnn.git
cd ncnn

# 编译工具
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release \
      -DNCNN_VULKAN=ON \
      -DNCNN_BUILD_TOOLS=ON \
      ..
make -j4

# 安装工具到系统路径
sudo cp tools/onnx/onnx2ncnn /usr/local/bin/
sudo cp tools/quantize/ncnn2int8 /usr/local/bin/
sudo cp tools/quantize/ncnn2table /usr/local/bin/
```

---

### 方案 6: 多线程并行优化⭐⭐⭐
**预期提升**: 10-20%（8 FPS → 8.8-9.6 FPS）
**难度**: 中等

#### 6.1 CPU 亲和性绑定
```python
import os

def _infer_loop(self) -> None:
    """推理线程：绑定到大核（性能核心）"""
    
    # 🔥 树莓派 4B 有 4 个 Cortex-A72 核心
    # 绑定推理线程到核心 2-3（避免与系统任务冲突）
    os.sched_setaffinity(0, {2, 3})
    
    logger.info("推理线程启动（绑定 CPU 2-3）")
    
    while not self._stop_event.is_set():
        # ... 推理逻辑 ...
```

#### 6.2 采集线程优化
```python
def _capture_loop(self) -> None:
    """采集线程：绑定到独立核心"""
    
    # 绑定到核心 0
    os.sched_setaffinity(0, {0})
    
    logger.info("采集线程启动（绑定 CPU 0）")
    
    while not self._stop_event.is_set():
        # ... 采集逻辑 ...
```

#### 6.3 设置线程优先级
```python
import ctypes

# Linux 系统调用
libc = ctypes.CDLL('libc.so.6')

def _infer_loop(self) -> None:
    # 提升推理线程优先级（需要 root 权限）
    try:
        # SCHED_FIFO 实时调度策略
        SCHED_FIFO = 1
        sched_param = ctypes.c_int(50)  # 优先级 50
        libc.sched_setscheduler(0, SCHED_FIFO, ctypes.byref(sched_param))
        logger.info("推理线程优先级已提升")
    except Exception as e:
        logger.warning(f"无法提升优先级: {e}（需要 sudo 运行）")
    
    # ... 推理逻辑 ...
```

---

### 方案 7: 系统级优化⭐⭐⭐⭐
**预期提升**: 5-15%（8 FPS → 8.4-9.2 FPS）
**难度**: 简单

#### 7.1 超频树莓派 CPU/GPU
```bash
# 编辑 /boot/config.txt
sudo nano /boot/config.txt

# 添加以下超频参数（安全范围内）
[all]
# CPU 超频：1.5GHz → 1.8GHz
over_voltage=4
arm_freq=1800

# GPU 超频：500MHz → 600MHz
gpu_freq=600

# 内存超频
sdram_freq=3200

# 温度限制（保护硬件）
temp_limit=80

# 保存后重启
sudo reboot

# 验证超频
vcgencmd measure_clock arm  # 查看 CPU 频率
vcgencmd measure_clock core # 查看 GPU 频率
vcgencmd measure_temp       # 查看温度
```

**⚠️ 警告**: 超频需要良好的散热（建议使用风扇或散热片），否则可能降频。

#### 7.2 禁用不必要的系统服务
```bash
# 禁用蓝牙（释放 CPU 资源）
sudo systemctl disable bluetooth
sudo systemctl stop bluetooth

# 禁用 WiFi（如果使用有线网络）
sudo systemctl disable wpa_supplicant
sudo systemctl stop wpa_supplicant

# 禁用图形界面（释放大量内存）
sudo systemctl set-default multi-user.target

# 重启到命令行模式
sudo reboot
```

#### 7.3 调整 Python 性能参数
```bash
# 设置环境变量（加入 ~/.bashrc）
export OMP_NUM_THREADS=4              # OpenMP 线程数
export OPENBLAS_NUM_THREADS=4         # BLAS 库线程数
export MKL_NUM_THREADS=4              # Intel MKL 线程数
export NUMEXPR_NUM_THREADS=4          # NumPy 表达式线程数

# 禁用 Python GC 在推理时（高级）
export PYTHONOPTIMIZE=2               # 启用优化模式
```

#### 7.4 使用 PyPy（Python JIT 编译器）
```bash
# 安装 PyPy3
sudo apt-get install pypy3 pypy3-dev

# 安装依赖（使用 PyPy 的 pip）
pypy3 -m pip install opencv-python ultralytics

# 使用 PyPy 运行程序
pypy3 src/main.py
```

---

## 🎯 综合优化方案（推荐组合）

### 🥇 方案 A：最佳性价比（预期 15+ FPS）
1. ✅ **降低输入分辨率** 到 320×320（+40%）
2. ✅ **启用 GPU 加速**（+30%）
3. ✅ **使用 FP16 模型**（+20%）
4. ✅ **系统超频**（+10%）

**总提升**: 8 × 1.4 × 1.3 × 1.2 × 1.1 = **16.5 FPS**

### 🥈 方案 B：极致性能（预期 20+ FPS）
1. ✅ 方案 A 的所有优化
2. ✅ **INT8 量化**（额外 +30%）
3. ✅ **自定义 NCNN Vulkan 推理**（额外 +20%）

**总提升**: 16.5 × 1.3 × 1.2 = **25.7 FPS**

### 🥉 方案 C：平衡方案（预期 12 FPS）
1. ✅ **降低分辨率**（+40%）
2. ✅ **FP16 模型**（+20%）
3. ✅ **多线程绑定**（+10%）

**总提升**: 8 × 1.4 × 1.2 × 1.1 = **14.8 FPS**

---

## 📝 实施优先级

### 第一阶段（1-2 小时）
1. 降低输入分辨率到 320×320
2. 启用摄像头硬件加速（MJPEG + 缓冲优化）
3. 重新导出 FP16 NCNN 模型

### 第二阶段（半天）
1. 配置 GPU 内存分配
2. 系统超频和服务优化
3. 多线程 CPU 绑定

### 第三阶段（1-2 天）
1. INT8 量化（需要采集校准数据）
2. 自定义 NCNN Vulkan 推理器
3. 编译优化的 OpenCV（可选）

---

## 🔍 性能监控工具

### 实时监控脚本
创建 `tools/monitor_performance.py`:

```python
"""
实时监控树莓派性能
"""
import subprocess
import time
import os

def get_cpu_freq():
    """获取 CPU 频率"""
    result = subprocess.run(['vcgencmd', 'measure_clock', 'arm'], 
                          capture_output=True, text=True)
    freq = int(result.stdout.split('=')[1]) / 1000000
    return f"{freq:.0f} MHz"

def get_gpu_freq():
    """获取 GPU 频率"""
    result = subprocess.run(['vcgencmd', 'measure_clock', 'core'], 
                          capture_output=True, text=True)
    freq = int(result.stdout.split('=')[1]) / 1000000
    return f"{freq:.0f} MHz"

def get_temp():
    """获取温度"""
    result = subprocess.run(['vcgencmd', 'measure_temp'], 
                          capture_output=True, text=True)
    return result.stdout.split('=')[1].strip()

def get_memory():
    """获取内存使用"""
    with open('/proc/meminfo', 'r') as f:
        lines = f.readlines()
    total = int(lines[0].split()[1]) / 1024  # MB
    available = int(lines[2].split()[1]) / 1024
    used = total - available
    return f"{used:.0f}/{total:.0f} MB ({used/total*100:.1f}%)"

def main():
    print("=" * 60)
    print("树莓派性能实时监控")
    print("=" * 60)
    
    while True:
        os.system('clear')
        print(f"⏰ 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔥 CPU 频率: {get_cpu_freq()}")
        print(f"🎮 GPU 频率: {get_gpu_freq()}")
        print(f"🌡️  温度: {get_temp()}")
        print(f"💾 内存: {get_memory()}")
        print("\n按 Ctrl+C 退出")
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n监控已停止")
```

---

## ⚠️ 注意事项

1. **散热**: 超频和高负载运行时，必须使用散热片或风扇
2. **电源**: 使用官方 5V/3A 电源适配器，避免欠压
3. **备份**: 优化前备份 `/boot/config.txt` 和重要数据
4. **测试**: 每次优化后使用 `test_annotation.py` 验证效果
5. **稳定性**: INT8 量化可能轻微降低精度，需在实际场景测试

---

## 📚 参考资源

- [NCNN 官方文档](https://github.com/Tencent/ncnn)
- [Raspberry Pi 超频指南](https://www.raspberrypi.com/documentation/computers/config_txt.html#overclocking)
- [Ultralytics YOLOv8 导出文档](https://docs.ultralytics.com/modes/export/)
- [OpenCV VideoCapture 优化](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html)

---

## 🎉 预期最终效果

| 优化阶段 | 推理帧率 | 延迟 | CPU 使用率 |
|----------|----------|------|------------|
| 基线 (NCNN) | 8 FPS | 125ms | 95% |
| 方案 C | 12 FPS | 83ms | 85% |
| 方案 A | 15 FPS | 67ms | 80% |
| 方案 B | 20+ FPS | 50ms | 75% |

**目标达成**：15+ FPS 可满足 RoboMaster 自瞄系统实时性要求！🚀
