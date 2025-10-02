#!/usr/bin/env python3
"""
通用 YOLOv8 PT 模型转 ONNX 模型脚本
支持自动检测 model/ 文件夹中的 .pt 文件并转换为 ONNX 格式
"""

import sys
import argparse
from pathlib import Path

try:
    from ultralytics import YOLO
except ImportError:
    print("❌ 未安装 ultralytics")
    print("安装: pip install ultralytics")
    sys.exit(1)

def convert_pt_to_onnx(
    pt_file: str = "yolov8n.pt",
    output_dir: str = "./model/",
    img_height: int = 480,
    img_width: int = 320,
    simplify: bool = True,
    opset: int = 12
):
    """
    将 PT 模型转换为 ONNX 模型
    
    Args:
        pt_file: PT 模型文件名（默认在 model/ 目录下）
        output_dir: 输出目录
        img_height: 模型输入高度
        img_width: 模型输入宽度
        simplify: 是否简化模型
        opset: ONNX opset 版本
    """
    
    # 构建完整路径
    model_dir = Path(output_dir)
    pt_path = model_dir / pt_file
    
    print("=" * 60)
    print("🔧 YOLOv8 PT → ONNX 转换工具")
    print("=" * 60)
    
    # 检查输入文件
    if not pt_path.exists():
        print(f"\n❌ 模型文件不存在: {pt_path}")
        print(f"\n请确保以下文件存在:")
        print(f"  {pt_path}")
        sys.exit(1)
    
    print(f"\n📦 输入模型: {pt_path}")
    print(f"📂 输出目录: {model_dir}")
    
    # 加载模型
    try:
        model = YOLO(str(pt_path))
        print("✅ 模型加载成功")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        sys.exit(1)
    
    # 配置信息
    print("\n🔥 转换配置:")
    print(f"  格式: ONNX")
    print(f"  输入尺寸: {img_height}×{img_width} (高×宽)")
    print(f"  简化模型: {simplify}")
    print(f"  ONNX opset: {opset}")
    print(f"  动态输入: False (固定尺寸，更快)")
    
    try:
        # 导出 ONNX 模型
        print("\n🚀 开始转换...")
        export_path = model.export(
            format='onnx',              # ONNX 格式
            simplify=simplify,          # 简化计算图
            dynamic=False,              # 固定输入尺寸（更快）
            opset=opset,                # ONNX opset 版本
            imgsz=(img_height, img_width),  # 输入尺寸 (高, 宽)
        )
        
        print(f"\n✅ 转换成功: {export_path}")
        
        # 检查文件大小
        export_path_obj = Path(export_path)
        size_mb = export_path_obj.stat().st_size / (1024 * 1024)
        print(f"📊 模型大小: {size_mb:.2f} MB")
        
        # 使用说明
        print("\n" + "=" * 60)
        print("📝 使用说明:")
        print("=" * 60)
        print("1. 在代码中加载模型:")
        print("   from ultralytics import YOLO")
        print(f"   model = YOLO('{export_path}')")
        print("   results = model.predict(frame)")
        print("\n2. 预期性能 (树莓派 4B):")
        print(f"   - 输入尺寸: {img_height}×{img_width}")
        
        # 根据分辨率估算性能
        pixels = img_height * img_width
        if pixels <= 100000:  # 320×240 = 76,800
            print("   - 推理时间: 100-150ms")
            print("   - FPS: 7-10")
        elif pixels <= 160000:  # 480×320 = 153,600
            print("   - 推理时间: 150-250ms")
            print("   - FPS: 4-7")
        else:  # 640×480 = 307,200
            print("   - 推理时间: 250-400ms")
            print("   - FPS: 2.5-4")
        
        print("   - 内存占用: ~200-300MB")
        print("=" * 60)
        
        return export_path
        
    except Exception as e:
        print(f"\n❌ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="YOLOv8 PT 模型转 ONNX 模型",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认配置 (yolov8n.pt → yolov8n.onnx, 480×320)
  python convert_pt_to_onnx.py
  
  # 指定模型文件
  python convert_pt_to_onnx.py --pt yolov8s.pt
  
  # 自定义分辨率
  python convert_pt_to_onnx.py --height 640 --width 480
  
  # 指定输出目录
  python convert_pt_to_onnx.py --output ./models/
        """
    )
    
    parser.add_argument(
        '--pt', 
        type=str, 
        default='yolov8n.pt',
        help='PT 模型文件名 (默认: yolov8n.pt，位于 model/ 目录)'
    )
    
    parser.add_argument(
        '--output', 
        type=str, 
        default='./model/',
        help='输出目录 (默认: ./model/)'
    )
    
    parser.add_argument(
        '--height', 
        type=int, 
        default=480,
        help='模型输入高度 (默认: 480)'
    )
    
    parser.add_argument(
        '--width', 
        type=int, 
        default=320,
        help='模型输入宽度 (默认: 320)'
    )
    
    parser.add_argument(
        '--no-simplify',
        action='store_true',
        help='不简化模型 (默认会简化)'
    )
    
    parser.add_argument(
        '--opset',
        type=int,
        default=12,
        help='ONNX opset 版本 (默认: 12)'
    )
    
    args = parser.parse_args()
    
    convert_pt_to_onnx(
        pt_file=args.pt,
        output_dir=args.output,
        img_height=args.height,
        img_width=args.width,
        simplify=not args.no_simplify,
        opset=args.opset
    )

if __name__ == "__main__":
    main()
