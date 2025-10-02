#
# demo_vision.py
# 视觉识别系统演示工具
#
# 功能：
#   - SSH 环境：无显示测试，输出检测统计
#   - 桌面/VNC 环境：可视化展示检测结果
#   - 实时性能监控：FPS、检测率等指标
#
# @author n1ghts4kura
#

import time
import cv2
import os
from src.recognizer import Recognizer

# 检测是否有显示环境（用于判断是否调用 cv2.waitKey）
HAS_DISPLAY = os.environ.get('DISPLAY') is not None

def main():
    print("=" * 60)
    print("RMYC Raspi Framework - 视觉识别演示")
    print("=" * 60)
    print("功能：实时目标检测与性能监控")
    print("操作：按 'q' 键退出程序 (仅桌面环境)")
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
    last_predict_count = 0  # 🔥 记录上次的推理帧数
    
    try:
        while True:
            # 显示环境：展示检测画面
            if HAS_DISPLAY:
                recognizer.imshow()
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
            
            # 智能休眠：推理未更新时释放 CPU
            if status['predict_frame_count'] == last_predict_count:
                time.sleep(0.01)
            else:
                last_predict_count = status['predict_frame_count']
            
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
                
                last_print_time = current_time
            
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
        print("🔬 推理性能")
        print("-" * 60)
        print(f"推理帧数: {final_status['predict_frame_count']}")
        print(f"推理帧率: {final_status['actual_inference_fps']:.2f} FPS")
        print(f"丢帧数: {final_status['dropped_frame_count']} (智能跳帧)")
        print()
        print("🎯 检测统计")
        print("-" * 60)
        print(f"检测到目标: {detect_count} 帧 ({detect_rate:.1f}%)")
        print("=" * 60)
        print("👋 程序结束")

if __name__ == "__main__":
    main()
