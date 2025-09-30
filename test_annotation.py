#
# test_main.py
#

import time
import cv2
from src.recognizer import Recognizer

def main():
    print("启动 Recognizer 测试程序...")
    
    with Recognizer() as recognizer:
        print("等待识别器初始化...")
        
        # 等待初始化完成
        if not recognizer.wait_until_initialized(timeout=30):
            print("初始化超时，退出程序")
            return
        
        print("初始化完成，开始检测...")
        print("按 'q' 键退出程序")
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                # 显示推理结果
                recognizer.imshow()
                
                # 检查退出键
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("用户请求退出")
                    break
                
                # 获取检测结果
                boxes = recognizer.get_latest_boxes()
                fps_info = recognizer.get_fps_info()
                
                # 每10帧输出一次统计信息
                frame_count += 1
                if frame_count % 10 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    
                    print(f"帧数: {frame_count:4d} | "
                          f"FPS: {fps:5.1f} | "
                          f"检测到目标: {len(boxes):2d} | "
                          f"队列: {fps_info['queue_size']}/{fps_info['max_queue_size']}")
                    
                    # 如果有检测到目标，显示详细信息
                    if boxes:
                        print(f"  边界框: {boxes}")
                
                time.sleep(0.05)  # 控制主循环频率
                
        except KeyboardInterrupt:
            print("\n检测到 Ctrl+C，正在退出...")
        except Exception as e:
            print(f"运行时异常: {e}")
        finally:
            print("程序结束")

if __name__ == "__main__":
    main()
