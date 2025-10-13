#!/usr/bin/env python3
"""
数据采集工具 (Data Collector)
整合焦距调整和数据采集功能，用于YOLO模型训练数据采集

功能:
- 高清预览 (1280x720)
- 拍照保存 (Gamma校正预处理)
- 视频录制 (MJPG编码，树莓派兼容)
- 焦距调整辅助 (十字准线)
- 实时状态显示

作者: RMYC Framework Team
日期: 2025-10-12
"""

import cv2
import os
import sys
import time
import numpy as np
from datetime import datetime

# 添加项目路径以导入 config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src import config
from src.utils import adjust_gamma
from typing import Optional, Tuple

class DataCollector:
    """数据采集工具类"""
    
    def __init__(
        self,
        camera_index: int = 0,
        width: int = 1280,
        height: int = 720,
        imshow_width: int = 1280,
        imshow_height: int = 720,
        fps: int = 120,
        save_dir: str = "training/captured",
        gamma: float = 1.3
    ):
        """
        初始化数据采集器
        
        Args:
            camera_index: 摄像头索引
            width: 分辨率宽度
            height: 分辨率高度
            fps: 目标帧率
            save_dir: 保存目录
            gamma: Gamma校正值
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.imshow_width = imshow_width
        self.imshow_height = imshow_height
        self.target_fps = fps
        self.save_dir = save_dir
        # 从配置文件读取 gamma 值（如果未指定）
        if gamma is not None:
            gamma = config.IMAGE_PREPROCESSING_GAMMA if config.ENABLE_IMAGE_PREPROCESSING else 1.0
        self.gamma = gamma
        
        # 状态变量
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.is_recording = False
        self.video_writer: Optional[cv2.VideoWriter] = None
        
        # 统计变量
        self.frame_count = 0
        self.saved_photo_count = 0
        self.saved_video_count = 0
        self.start_time = 0.0
        self.recording_start_time = 0.0
        
        # 创建保存目录
        os.makedirs(self.save_dir, exist_ok=True)
        print(f"📁 保存目录: {os.path.abspath(self.save_dir)}")
    
    def _init_camera(self) -> bool:
        """
        初始化摄像头（支持索引重试）
        
        Returns:
            是否成功初始化
        """
        while True:
            print(f"🔍 尝试打开摄像头 (索引: {self.camera_index})...")
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                print(f"❌ 无法打开摄像头 {self.camera_index}")
                print("💡 提示: 使用 `ls /dev/video*` 或 `v4l2-ctl --list-devices` 查看可用设备")
                
                try:
                    new_index = input("请输入新的摄像头索引 (或按 Ctrl+C 退出): ")
                    self.camera_index = int(new_index)
                except (ValueError, KeyboardInterrupt):
                    print("\n👋 退出程序")
                    return False
                continue
            
            # 设置分辨率和帧率
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)

            time.sleep(0.5)  # 等待摄像头稳定
            
            # 验证实际参数
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            print(f"✅ 摄像头初始化成功")
            print(f"📐 设置分辨率: {self.width}x{self.height}")
            print(f"📐 实际分辨率: {actual_width}x{actual_height}")
            if actual_fps > 0:
                print(f"🎬 帧率: {actual_fps:.1f} FPS")
            
            self.is_running = True
            return True
    
    def _apply_preprocessing(self, frame: np.ndarray) -> np.ndarray:
        """
        应用预处理（Gamma校正）
        
        Args:
            frame: 原始帧
        
        Returns:
            预处理后的帧
        """
        return adjust_gamma(frame, gamma=self.gamma)
    
    def capture_photo(self, frame: np.ndarray) -> bool:
        """
        拍照并保存（应用Gamma校正）
        
        Args:
            frame: 当前帧
        
        Returns:
            是否成功保存
        """
        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}.jpg"
            filepath = os.path.join(self.save_dir, filename)
            
            # 保存图像（frame 已经过 gamma 处理）
            success = cv2.imwrite(filepath, frame)
            
            if success:
                self.saved_photo_count += 1
                print(f"\n📷 照片已保存: {filepath} (第 {self.saved_photo_count} 张)")
                return True
            else:
                print(f"\n❌ 保存失败: {filepath}")
                return False
        
        except Exception as e:
            print(f"\n❌ 拍照时出错: {e}")
            return False
    
    def start_recording(self) -> bool:
        """
        开始录像（使用MJPG编码）
        
        Returns:
            是否成功启动录制
        """
        if self.is_recording:
            print("\n⚠️ 已在录制中")
            return False
        
        try:
            # 生成文件名（使用 .avi 格式配合 MJPG）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}.avi"
            filepath = os.path.join(self.save_dir, filename)
            
            # 使用 MJPG 编码（树莓派广泛支持）
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            
            # 创建 VideoWriter
            self.video_writer = cv2.VideoWriter(
                filepath,
                fourcc,
                self.target_fps,
                (self.width, self.height)
            )
            
            if self.video_writer.isOpened():
                self.is_recording = True
                self.recording_start_time = time.time()
                self.saved_video_count += 1
                print(f"\n🔴 开始录制: {filepath}")
                return True
            else:
                print(f"\n❌ 录制失败: 无法初始化 VideoWriter")
                self.video_writer = None
                return False
        
        except Exception as e:
            print(f"\n❌ 启动录制时出错: {e}")
            self.video_writer = None
            return False
    
    def stop_recording(self) -> bool:
        """
        停止录像
        
        Returns:
            是否成功停止
        """
        if not self.is_recording:
            print("\n⚠️ 当前未在录制")
            return False
        
        try:
            if self.video_writer is not None:
                self.video_writer.release()
                self.video_writer = None
            
            recording_duration = time.time() - self.recording_start_time
            self.is_recording = False
            
            print(f"\n⏹️ 录制结束 (时长: {recording_duration:.1f}s)")
            return True
        
        except Exception as e:
            print(f"\n❌ 停止录制时出错: {e}")
            return False
    
    def _write_frame(self, frame: np.ndarray) -> None:
        """
        写入视频帧
        
        Args:
            frame: 要写入的帧
        """
        if self.video_writer is not None and self.is_recording:
            self.video_writer.write(frame)
    
    def _draw_ui(self, frame: np.ndarray) -> np.ndarray:
        """
        绘制UI叠加层（十字准线、状态信息）
        
        Args:
            frame: 原始帧
        
        Returns:
            绘制后的帧
        """
        ui_frame = frame.copy()
        height, width = ui_frame.shape[:2]
        
        # 绘制十字准线（帮助对焦）
        cv2.line(ui_frame, (width//2, 0), (width//2, height), (0, 255, 0), 1)
        cv2.line(ui_frame, (0, height//2), (width, height//2), (0, 255, 0), 1)
        
        # 显示分辨率
        cv2.putText(
            ui_frame,
            f"Resolution: {width}x{height}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        # 显示实时帧率
        if self.frame_count > 0 and self.start_time > 0:
            elapsed = time.time() - self.start_time
            current_fps = self.frame_count / elapsed
            cv2.putText(
                ui_frame,
                f"FPS: {current_fps:.1f}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
        
        # 显示录制状态
        if self.is_recording:
            # 红色 "REC" 标识
            cv2.putText(
                ui_frame,
                "REC",
                (width - 100, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                3
            )
            # 红色圆点（闪烁效果）
            if int(time.time() * 2) % 2 == 0:
                cv2.circle(ui_frame, (width - 120, 30), 10, (0, 0, 255), -1)
        
        # 显示操作提示
        cv2.putText(
            ui_frame,
            "C:Photo | R:Record | I:Info | Q:Quit",
            (10, height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )
        
        return cv2.resize(ui_frame, (self.imshow_width, self.imshow_height))
    
    def run(self) -> None:
        """主循环 - 运行数据采集器"""
        print("\n" + "="*70)
        print("📊 数据采集工具 (Data Collector)")
        print("="*70)
        print("功能说明:")
        print("  📷 拍照: 按 'C' 或 'S' 键 (应用Gamma校正)")
        print("  🎬 录像: 按 'R' 键开始/停止录制 (MJPG编码)")
        print("  📐 焦距: 观察十字准线区域清晰度")
        print("  ℹ️  信息: 按 'I' 键查看图像详细信息")
        print("  ❌ 退出: 按 'Q' 键")
        print("="*70 + "\n")
        
        # 初始化摄像头
        if not self._init_camera():
            return
        
        # 重置统计
        self.frame_count = 0
        self.start_time = time.time()
        
        try:
            while self.is_running:
                ret, frame = self.cap.read()
                
                if not ret:
                    print("⚠️ 无法读取帧")
                    break
                
                self.frame_count += 1
                
                # 如果正在录制，写入预处理后的帧
                if self.is_recording:
                    processed_frame = self._apply_preprocessing(frame)
                    self._write_frame(processed_frame)
                
                # 绘制UI叠加层
                display_frame = self._draw_ui(frame)
                
                # 显示画面
                cv2.imshow('Data Collector - Preview', display_frame)
                
                # 按键处理
                key = cv2.waitKey(10) & 0xFF  # 增加等待时间以减少CPU占用
                
                if key == ord('q') or key == ord('Q'):
                    print("\n👋 退出程序")
                    break
                
                elif key == ord('c') or key == ord('C') or key == ord('s') or key == ord('S'):
                    self.capture_photo(frame)
                
                elif key == ord('r') or key == ord('R'):
                    if self.is_recording:
                        self.stop_recording()
                    else:
                        self.start_recording()
                
                elif key == ord('i') or key == ord('I'):
                    print(f"\n📸 图像信息:")
                    print(f"  - 形状: {frame.shape}")
                    print(f"  - 数据类型: {frame.dtype}")
                    print(f"  - 平均亮度: {frame.mean():.1f}")
                    print(f"  - 亮度范围: [{frame.min()}, {frame.max()}]")
                    print(f"  - Gamma校正值: {self.gamma}")
        
        except KeyboardInterrupt:
            print("\n\n⚠️ 检测到 Ctrl+C")
        
        except Exception as e:
            print(f"\n❌ 运行时错误: {e}")
        
        finally:
            self._cleanup()
    
    def _cleanup(self) -> None:
        """清理资源"""
        print("\n🧹 正在清理资源...")
        
        # 停止录制
        if self.is_recording:
            self.stop_recording()
        
        # 释放摄像头
        if self.cap is not None:
            self.cap.release()
        
        # 关闭窗口
        cv2.destroyAllWindows()
        
        # 显示统计信息
        total_time = time.time() - self.start_time
        avg_fps = self.frame_count / total_time if total_time > 0 else 0
        
        print("\n" + "="*70)
        print("📊 运行统计")
        print("="*70)
        print(f"  总帧数: {self.frame_count}")
        print(f"  运行时间: {total_time:.1f}s")
        print(f"  平均帧率: {avg_fps:.1f} FPS")
        print(f"  拍摄照片: {self.saved_photo_count} 张")
        print(f"  录制视频: {self.saved_video_count} 个")
        print(f"  保存位置: {os.path.abspath(self.save_dir)}")
        print("="*70)
        
        self.is_running = False

def main():
    """主函数"""
    # 创建数据采集器（可自定义参数）
    collector = DataCollector(
        camera_index=0,      # 摄像头索引
        width=1280,          # 分辨率宽度
        height=720,          # 分辨率高度
        fps=30,              # 帧率
        save_dir="training/captured",  # 保存目录
        gamma=1.3            # Gamma校正值
    )
    
    # 运行采集器
    collector.run()

if __name__ == "__main__":
    main()
