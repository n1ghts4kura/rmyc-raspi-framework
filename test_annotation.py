#
# test_annotation.py
# 视觉识别器测试程序
#
# @author n1ghts4kura
#

import time
import cv2
from src.recognizer import Recognizer

def main():
    print("=" * 60)
    print("RMYC Raspi Framework - Recognizer 测试程序")
    print("=" * 60)
    print("功能：测试 YOLOv8 目标检测的实时性能和准确性")
    print("操作：按 'q' 键退出程序")
    print("=" * 60)
    print()
    
    # 获取单例实例
    print("📷 正在初始化识别器（单例模式）...")
    recognizer = Recognizer.get_instance()
    
    # 等待初始化完成（包含模型预热）
    print("⏳ 等待识别器就绪（首次启动需要模型预热，约 5-10 秒）...")
    if not recognizer.wait_until_initialized(timeout=30):
        print("❌ 初始化超时（30秒），退出程序")
        return
    
    # 检查运行状态
    if not recognizer.is_running():
        print("❌ 识别器未正常运行，退出程序")
        return
    
    # 显示详细状态
    status = recognizer.get_status()
    print("✅ 识别器初始化完成（模型已预热）")
    print(f"   - 摄像头：{'已打开' if status['camera_opened'] else '未打开'}")
    print(f"   - 模型：{'已加载并预热' if status['model_loaded'] else '未加载'}")
    print(f"   - 采集线程：{'运行中' if status['capture_thread_alive'] else '未运行'}")
    print(f"   - 推理线程：{'运行中' if status['infer_thread_alive'] else '未运行'}")
    print(f"   - 推理模式：最大速度模式（无帧率限制）")
    print()
    
    print("🎬 开始实时检测...")
    print("-" * 60)
    
    frame_count = 0
    detect_count = 0
    start_time = time.time()
    last_print_time = start_time
    
    try:
        while True:
            # 显示推理结果（如果启用了注释帧）
            recognizer.imshow()
            
            # 检查退出键
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n👋 用户请求退出")
                break
            
            # 获取检测结果
            boxes = recognizer.get_latest_boxes()
            status = recognizer.get_status()
            
            frame_count += 1
            if boxes:
                detect_count += 1
            
            # 每秒输出一次统计信息
            current_time = time.time()
            if current_time - last_print_time >= 1.0:
                elapsed = current_time - start_time
                avg_fps = frame_count / elapsed if elapsed > 0 else 0
                detect_rate = (detect_count / frame_count * 100) if frame_count > 0 else 0
                
                print(f"[{int(elapsed):4d}s] "
                      f"主循环帧数: {frame_count:5d} | "
                      f"推理帧数: {status['predict_frame_count']:5d} | "
                      f"丢弃帧数: {status['dropped_frame_count']:5d} | "
                      f"实际推理FPS: {status['actual_inference_fps']:5.2f} | "
                      f"检测率: {detect_rate:5.1f}% | "
                      f"当前目标: {len(boxes):2d}")
                
                # 如果有检测到目标，显示详细信息
                if boxes and len(boxes) <= 3:  # 最多显示3个目标的详细信息
                    for idx, box in enumerate(boxes, 1):
                        x1, y1, x2, y2 = box
                        width = x2 - x1
                        height = y2 - y1
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2
                        print(f"      目标 {idx}: 中心({center_x:.0f}, {center_y:.0f}) "
                              f"尺寸({width:.0f}x{height:.0f})")
                
                last_print_time = current_time
            
            time.sleep(0.01)  # 控制主循环频率，避免 CPU 占用过高
            
    except KeyboardInterrupt:
        print("\n⚠️  检测到 Ctrl+C 信号")
    except Exception as e:
        print(f"\n❌ 运行时异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 最终统计
        total_time = time.time() - start_time
        final_status = recognizer.get_status()
        avg_fps = frame_count / total_time if total_time > 0 else 0
        detect_rate = (detect_count / frame_count * 100) if frame_count > 0 else 0
        
        print()
        print("=" * 60)
        print("📊 测试统计")
        print("=" * 60)
        print(f"总运行时间: {total_time:.1f} 秒")
        print(f"主循环总帧数: {frame_count}")
        print(f"主循环平均 FPS: {avg_fps:.2f}")
        print()
        print("🔬 推理性能统计")
        print("-" * 60)
        print(f"推理总帧数: {final_status['predict_frame_count']}")
        print(f"丢弃总帧数: {final_status['dropped_frame_count']}")
        print(f"实际推理帧率: {final_status['actual_inference_fps']} FPS （最大速度）")
        
        # 计算推理效率
        if final_status['predict_frame_count'] > 0:
            inference_efficiency = (final_status['predict_frame_count'] / 
                                   (final_status['predict_frame_count'] + final_status['dropped_frame_count']) * 100)
            print(f"推理效率: {inference_efficiency:.2f}%")
            print(f"   （推理帧数 / (推理帧数 + 丢弃帧数) × 100）")
            print()
            print(f"💡 性能指标：")
            print(f"   - 实际推理 FPS 越高越好（受硬件和模型限制）")
            print(f"   - 丢弃帧数正常（智能跳帧策略，确保处理最新图像）")
        
        print()
        print("🎯 目标检测统计")
        print("-" * 60)
        print(f"检测到目标的帧数: {detect_count}")
        print(f"目标检测率: {detect_rate:.2f}%")
        print("=" * 60)
        print("👋 程序结束")

if __name__ == "__main__":
    main()
