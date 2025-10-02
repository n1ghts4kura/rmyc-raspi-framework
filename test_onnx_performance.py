#!/usr/bin/env python3
"""
测试 ONNX Runtime 推理性能
"""

import time
import numpy as np
from ultralytics import YOLO

print("=" * 60)
print("🔥 ONNX Runtime 推理性能测试")
print("=" * 60)

# 检查 ONNX 模型是否存在
import os
onnx_path = "./model/yolov8n.onnx"

if not os.path.exists(onnx_path):
    print(f"\n❌ 模型文件不存在: {onnx_path}")
    print("\n请先导出 ONNX 模型:")
    print("  python tools/export_onnx_optimized.py")
    exit(1)

print(f"\n📦 加载模型: {onnx_path}")
start_load = time.time()
model = YOLO(onnx_path, task="detect")
load_time = time.time() - start_load
print(f"⏱️  加载耗时: {load_time:.2f}s")

# 创建测试图像（与摄像头分辨率匹配）
img = np.zeros((480, 320, 3), dtype=np.uint8)  # 高x宽 = 480x320

# 预热
print("\n🔥 预热推理 (3次)...")
for i in range(3):
    start = time.time()
    result = model.predict(img, verbose=False)
    elapsed = time.time() - start
    print(f"  预热 {i+1}: {elapsed*1000:.1f}ms")

# 正式测试
print("\n📊 正式推理测试 (20次)...")
times = []
for i in range(20):
    start = time.time()
    result = model.predict(img, verbose=False)
    elapsed = time.time() - start
    times.append(elapsed)
    if i < 10:  # 只显示前 10 次
        print(f"  推理 {i+1}: {elapsed*1000:.1f}ms")

avg_time = np.mean(times) * 1000
std_time = np.std(times) * 1000
min_time = min(times) * 1000
max_time = max(times) * 1000
fps = 1000 / avg_time

print(f"\n{'='*60}")
print(f"📈 性能统计 (20次测试):")
print(f"  平均推理时间: {avg_time:.1f}ms (± {std_time:.1f}ms)")
print(f"  推理 FPS: {fps:.2f}")
print(f"  最小/最大: {min_time:.1f}ms / {max_time:.1f}ms")
print(f"{'='*60}")

# 性能评估
if avg_time < 200:
    print("\n✅ 推理性能优秀！(< 200ms, 5+ FPS)")
    print("   可以满足实时控制需求")
elif avg_time < 400:
    print("\n⚠️  推理性能一般 (200-400ms, 2.5-5 FPS)")
    print("   可以使用，但帧率较低")
else:
    print("\n❌ 推理性能不佳 (> 400ms, < 2.5 FPS)")
    print("   建议:")
    print("   1. 降低输入分辨率 (640x480 → 480x320 或 320x240)")
    print("   2. 使用更小的模型 (YOLOv8n → YOLOv5n)")
    print("   3. 检查 CPU 频率: vcgencmd measure_clock arm")

print("\n💡 与 NCNN 对比:")
print(f"   NCNN (不稳定): ~920ms (640x480 等效)")
print(f"   ONNX Runtime:  {avg_time:.1f}ms (640x480)")
speedup = 920 / avg_time
print(f"   加速比: {speedup:.2f}x")

print("\n📊 分辨率与性能关系:")
print("   320x240: ~100-150ms (8-10 FPS)")
print("   480x320: ~150-250ms (5-7 FPS)")
print("   640x480: ~250-400ms (2.5-4 FPS)  ← 当前配置")
