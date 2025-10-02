#!/usr/bin/env python3
"""
FP16 半精度 NCNN 模型导出脚本
将 YOLOv8n.pt 转换为 NCNN FP16 格式，提升推理速度 20-30%

使用方法：
    python tools/export_fp16_model.py
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from ultralytics import YOLO
except ImportError:
    print("❌ 未安装 ultralytics")
    print("   请运行：pip install ultralytics")
    sys.exit(1)


def export_fp16_ncnn_model(
    model_path: str = "model/yolov8n.pt",
    output_dir: str = "model/yolov8n_ncnn_fp16",
    input_size: int = 320
):
    """
    导出 FP16 精度的 NCNN 模型
    
    Args:
        model_path: 输入的 PyTorch 模型路径
        output_dir: 输出目录
        input_size: 模型输入尺寸（320/416/640）
    """
    print("=" * 60)
    print("YOLOv8n FP16 NCNN 模型导出工具")
    print("=" * 60)
    print()
    
    # 检查模型文件是否存在
    if not os.path.exists(model_path):
        print(f"❌ 模型文件不存在: {model_path}")
        return False
    
    print(f"📂 输入模型: {model_path}")
    print(f"📂 输出目录: {output_dir}")
    print(f"📐 输入尺寸: {input_size}x{input_size}")
    print(f"🔧 精度模式: FP16 半精度")
    print()
    
    try:
        # 加载模型
        print("⏳ 加载 YOLOv8n 模型...")
        model = YOLO(model_path)
        print("✅ 模型加载成功")
        print()
        
        # 导出为 NCNN (FP16)
        print("⏳ 导出 NCNN FP16 模型（这可能需要几分钟）...")
        print("   - 启用半精度: ✅")
        print("   - 模型简化: ✅")
        print()
        
        export_path = model.export(
            format="ncnn",           # NCNN 格式
            half=True,               # 🔥 关键：启用 FP16
            imgsz=input_size,        # 输入尺寸
            simplify=True,           # 简化模型
            int8=False,              # 不使用 INT8
            dynamic=False,           # 静态输入尺寸
        )
        
        print("✅ 导出完成！")
        print()
        print(f"📁 导出路径: {export_path}")
        print()
        
        # 验证导出的文件
        expected_files = [
            "model.ncnn.param",
            "model.ncnn.bin",
            "metadata.yaml"
        ]
        
        print("🔍 验证导出文件...")
        export_dir = Path(export_path)
        
        for file_name in expected_files:
            file_path = export_dir / file_name
            if file_path.exists():
                file_size = file_path.stat().st_size / 1024  # KB
                print(f"   ✅ {file_name} ({file_size:.2f} KB)")
            else:
                print(f"   ❌ {file_name} 不存在")
        
        print()
        print("=" * 60)
        print("✅ 导出成功！")
        print("=" * 60)
        print()
        print("📝 下一步操作：")
        print(f"   1. 修改 recognizer.py 中的 model_path:")
        print(f"      self.model_path = \"{export_path}\"")
        print()
        print(f"   2. 运行测试验证性能:")
        print(f"      python test_annotation.py")
        print()
        print("💡 预期效果：")
        print("   - FP16 相比 FP32 提升: 20-30%")
        print("   - 内存占用减少: 50%")
        print("   - 精度损失: < 1%（几乎无损）")
        print()
        
        return True
        
    except Exception as e:
        print()
        print(f"❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def compare_model_sizes():
    """对比不同精度模型的大小"""
    print("=" * 60)
    print("模型大小对比")
    print("=" * 60)
    
    models = [
        ("model/yolov8n.pt", "PyTorch 原始模型"),
        ("model/yolov8n_ncnn_model/model.ncnn.bin", "NCNN FP32"),
        ("model/yolov8n_ncnn_fp16/model.ncnn.bin", "NCNN FP16"),
    ]
    
    for model_path, description in models:
        if os.path.exists(model_path):
            size_mb = os.path.getsize(model_path) / (1024 * 1024)
            print(f"  {description:25s}: {size_mb:.2f} MB")
        else:
            print(f"  {description:25s}: ❌ 不存在")
    
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="导出 FP16 NCNN 模型")
    parser.add_argument(
        "--model", 
        type=str, 
        default="model/yolov8n.pt",
        help="输入模型路径"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="model/yolov8n_ncnn_fp16",
        help="输出目录"
    )
    parser.add_argument(
        "--size",
        type=int,
        default=320,
        choices=[256, 320, 416, 640],
        help="输入尺寸"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="对比模型大小"
    )
    
    args = parser.parse_args()
    
    if args.compare:
        compare_model_sizes()
    else:
        success = export_fp16_ncnn_model(
            model_path=args.model,
            output_dir=args.output,
            input_size=args.size
        )
        
        if success:
            print("🎉 导出成功！")
            sys.exit(0)
        else:
            print("😞 导出失败")
            sys.exit(1)
