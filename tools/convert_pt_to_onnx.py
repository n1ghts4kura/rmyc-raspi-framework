#!/usr/bin/env python3
"""
通用 YOLOv8 PT 模型转 ONNX 模型脚本
支持交互式选择 model/ 文件夹中的 .pt 文件并转换为 ONNX 格式
"""

import sys
import argparse
from pathlib import Path
from typing import List

try:
    from ultralytics import YOLO
except ImportError:
    print("❌ 未安装 ultralytics")
    print("安装: pip install ultralytics")
    sys.exit(1)

def list_pt_models(model_dir: Path) -> List[Path]:
    """列出目录中所有 .pt 模型文件"""
    pt_files = sorted(model_dir.glob("*.pt"))
    return pt_files

def select_model_interactive(model_dir: Path) -> Path:
    """交互式选择模型文件"""
    pt_files = list_pt_models(model_dir)
    
    if not pt_files:
        print(f"❌ 在 {model_dir} 中未找到 .pt 模型文件")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("📦 可用的 PT 模型文件:")
    print("=" * 60)
    
    for i, pt_file in enumerate(pt_files, 1):
        size_mb = pt_file.stat().st_size / (1024 * 1024)
        print(f"  [{i}] {pt_file.name:<30} ({size_mb:.2f} MB)")
    
    print("=" * 60)
    
    while True:
        try:
            choice = input(f"\n请选择模型 [1-{len(pt_files)}] (或输入文件名): ").strip()
            
            # 尝试作为数字解析
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(pt_files):
                    return pt_files[idx]
                else:
                    print(f"❌ 请输入 1-{len(pt_files)} 之间的数字")
            # 尝试作为文件名解析
            else:
                # 自动添加 .pt 后缀
                if not choice.endswith('.pt'):
                    choice += '.pt'
                pt_path = model_dir / choice
                if pt_path.exists():
                    return pt_path
                else:
                    print(f"❌ 文件不存在: {choice}")
        except KeyboardInterrupt:
            print("\n\n❌ 用户取消操作")
            sys.exit(0)
        except Exception as e:
            print(f"❌ 输入错误: {e}")

def convert_pt_to_onnx(
    pt_path: Path,
    output_dir: Path,
    img_height: int = 480,
    img_width: int = 320,
    simplify: bool = True,
    opset: int = 12
):
    """
    将 PT 模型转换为 ONNX 模型
    
    Args:
        pt_path: PT 模型文件完整路径
        output_dir: 输出目录
        img_height: 模型输入高度
        img_width: 模型输入宽度
        simplify: 是否简化模型
        opset: ONNX opset 版本
    """
    
    # 生成 ONNX 文件名（与 PT 文件同名，但后缀为 .onnx）
    onnx_filename = pt_path.stem + ".onnx"
    onnx_path = output_dir / onnx_filename
    
    print("\n" + "=" * 60)
    print("🔧 YOLOv8 PT → ONNX 转换工具")
    print("=" * 60)
    
    print(f"\n📦 输入模型: {pt_path}")
    print(f"📂 输出路径: {onnx_path}")
    print(f"� 输入文件大小: {pt_path.stat().st_size / (1024*1024):.2f} MB")
    
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
        description="YOLOv8 PT 模型转 ONNX 模型（支持交互式选择）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互式选择模型（推荐）
  python convert_pt_to_onnx.py
  
  # 指定模型文件（跳过交互）
  python convert_pt_to_onnx.py --pt yolov8s.pt
  python convert_pt_to_onnx.py --pt detect.pt
  
  # 自定义分辨率
  python convert_pt_to_onnx.py --height 640 --width 480
  
  # 指定模型目录
  python convert_pt_to_onnx.py --model-dir ./models/
        """
    )
    
    parser.add_argument(
        '--pt', 
        type=str, 
        default=None,
        help='PT 模型文件名 (不指定则交互式选择)'
    )
    
    parser.add_argument(
        '--model-dir', 
        type=str, 
        default='./model/',
        help='模型目录 (默认: ./model/)'
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
    
    model_dir = Path(args.model_dir)
    
    # 检查模型目录
    if not model_dir.exists():
        print(f"❌ 模型目录不存在: {model_dir}")
        sys.exit(1)
    
    # 选择模型文件
    if args.pt:
        # 命令行指定模型
        pt_path = model_dir / args.pt
        if not pt_path.exists():
            print(f"❌ 模型文件不存在: {pt_path}")
            sys.exit(1)
    else:
        # 交互式选择
        pt_path = select_model_interactive(model_dir)
    
    # 执行转换
    convert_pt_to_onnx(
        pt_path=pt_path,
        output_dir=model_dir,
        img_height=args.height,
        img_width=args.width,
        simplify=not args.no_simplify,
        opset=args.opset
    )

if __name__ == "__main__":
    main()
