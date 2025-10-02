#
# recognizer.py
#
# @author n1ghts4kura
#

import typing as t
import threading
import time
import os
import cv2
import queue
import numpy as np
from ultralytics import YOLO

IF_IMSHOW = False # 是否显示窗口
IF_ANNOTATE = False # 是否生成带注释的帧（用于调试展示）

try:
    import src.logger as logger
except ImportError:
    import logger

class Recognizer:
    """
    单摄像头、单模型识别器
    
    采用双线程设计：采集线程专注高频采集，推理线程处理最新帧。
    
    **单例模式**：全局只允许存在一个 Recognizer 实例。
    
    用法：
        # 获取单例实例
        recog = Recognizer.get_instance()
        recog.wait_until_initialized()
        
        # 检查是否正在运行
        if recog.is_running():
            boxes = recog.get_latest_boxes()
        
        # 或使用上下文管理器
        with Recognizer.get_instance() as recog:
            recog.wait_until_initialized()
            boxes = recog.get_latest_boxes()
    """
    
    _instance: t.Optional['Recognizer'] = None
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """实现单例模式：确保全局只有一个实例"""
        if cls._instance is None:
            with cls._instance_lock:
                # 双重检查锁定
                if cls._instance is None:
                    cls._instance = super(Recognizer, cls).__new__(cls)
                    cls._instance._singleton_initialized = False
        return cls._instance

    def __init__(
        self,
        cam_width: int = 320,
        cam_height: int = 480,
        imshow_width: int = 160,
        imshow_height: int = 240,
        cam_fps: float = 60.0,
        target_inference_fps: int = 15,  # � 目标推理帧率（仅用于性能对比，不限制实际速度）
        model_input_size: int = 320,      # 🔥 YOLO 输入尺寸（256/320/416）
    ) -> None:
        # 避免重复初始化
        if self._singleton_initialized:
            return
        
        self._singleton_initialized = True
        # 摄像头配置
        self.cam_width = cam_width
        self.cam_height = cam_height
        self.cam_fps = cam_fps

        # 推理配置
        self.target_inference_fps = target_inference_fps  # � 目标推理帧率（用于性能对比）
        self.model_input_size = model_input_size  # 🔥 YOLO 输入尺寸

        # 显示配置
        self.imshow_width = imshow_width
        self.imshow_height = imshow_height
        
        # 模型配置
        self.model_path = "./model/yolov8n.onnx"  # 🔥 使用 ONNX 格式（比 NCNN 更稳定）
        self.conf: float = 0.3  # 降低置信度阈值
        self.iou: float = 0.7
        self.device: str = "cpu"  # 🔥 推理设备（cpu / 0 / 1 等）
        
        # 运行状态
        self._initialized: bool = False
        self._initialized_lock = threading.Lock()
        
        # 硬件资源
        self.cap: t.Optional[cv2.VideoCapture] = None
        self.model: t.Optional[YOLO] = None
        
        # 显示帧（用于可视化）
        self.current_annotated_frame: t.Optional[cv2.typing.MatLike] = None
        
        # 线程间通信
        self._frame_queue: queue.Queue = queue.Queue(maxsize=2)  # 增加队列大小
        self._capture_thread: t.Optional[threading.Thread] = None
        self._infer_thread: t.Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # 结果存储（线程安全）
        self._lock = threading.Lock()
        self._latest_boxes: t.List[t.List[float]] = []

        # 性能统计
        self._predict_frame_count = 0
        self._dropped_frame_count = 0
        self._last_inference_time = 0
        self._inference_start_time = 0  # 推理开始时间（用于计算平均 FPS）

        self.start()

    @classmethod
    def get_instance(cls, **kwargs) -> 'Recognizer':
        """
        获取 Recognizer 单例实例。
        
        Args:
            **kwargs: 仅在首次创建实例时有效，后续调用会忽略这些参数。
        
        Returns:
            Recognizer: 单例实例
        
        Example:
            >>> recog = Recognizer.get_instance(cam_width=640, cam_height=480)
            >>> # 后续调用返回同一实例
            >>> recog2 = Recognizer.get_instance()  # recog2 is recog -> True
        """
        if cls._instance is None:
            return cls(**kwargs)
        return cls._instance

    def is_running(self) -> bool:
        """
        检查识别器是否正在运行（采集线程和推理线程都在活跃状态）。
        
        Returns:
            bool: 如果采集线程和推理线程都在运行，返回 True；否则返回 False。
        
        Example:
            >>> recog = Recognizer.get_instance()
            >>> recog.start()
            >>> if recog.is_running():
            ...     boxes = recog.get_latest_boxes()
        """
        # 检查初始化状态
        with self._initialized_lock:
            if not self._initialized:
                return False
        
        # 检查线程是否存活且未停止
        capture_alive = (
            self._capture_thread is not None and 
            self._capture_thread.is_alive() and 
            not self._stop_event.is_set()
        )
        
        infer_alive = (
            self._infer_thread is not None and 
            self._infer_thread.is_alive() and 
            not self._stop_event.is_set()
        )
        
        return capture_alive and infer_alive
    
    def get_status(self) -> dict:
        """
        获取识别器的详细运行状态。
        
        Returns:
            dict: 包含以下字段的状态字典
                - initialized: 是否已初始化
                - running: 是否正在运行
                - capture_thread_alive: 采集线程是否存活
                - infer_thread_alive: 推理线程是否存活
                - stop_event_set: 停止事件是否已设置
                - queue_size: 当前队列大小
                - latest_boxes_count: 最新检测到的目标数量
                - predict_frame_count: 已推理的总帧数
                - dropped_frame_count: 已丢弃的帧数
                - target_inference_fps: 目标推理帧率（用于对比）
                - actual_inference_fps: 实际推理帧率
        
        Example:
            >>> recog = Recognizer.get_instance()
            >>> status = recog.get_status()
            >>> print(f"运行状态: {status['running']}, 检测目标数: {status['latest_boxes_count']}")
        """
        with self._initialized_lock:
            initialized = self._initialized
        
        capture_alive = self._capture_thread is not None and self._capture_thread.is_alive()
        infer_alive = self._infer_thread is not None and self._infer_thread.is_alive()
        
        # 计算实际推理帧率（基于启动以来的平均值）
        actual_fps = 0.0
        if self._inference_start_time > 0 and self._predict_frame_count > 0:
            elapsed = time.time() - self._inference_start_time
            if elapsed > 0:
                # 基于总推理帧数计算平均帧率
                actual_fps = self._predict_frame_count / elapsed
        
        return {
            "initialized": initialized,
            "running": self.is_running(),
            "capture_thread_alive": capture_alive,
            "infer_thread_alive": infer_alive,
            "stop_event_set": self._stop_event.is_set(),
            "queue_size": self._frame_queue.qsize(),
            "latest_boxes_count": len(self._latest_boxes),
            "camera_opened": self.cap is not None and (self.cap.isOpened() if self.cap else False),
            "model_loaded": self.model is not None,
            "predict_frame_count": self._predict_frame_count,
            "dropped_frame_count": self._dropped_frame_count,
            "target_inference_fps": self.target_inference_fps,
            "actual_inference_fps": round(actual_fps, 2),
        }


    def __del__(self):
        self.stop()
        self.clean_up()


    def wait_until_initialized(self, timeout: float = 120) -> bool:
        """
        阻塞等待，直到识别器初始化完成或超时。
        
        Args:
            timeout (float): 最大等待时间，单位秒。默认120秒。
        Returns:
            bool: 如果在超时前初始化完成，返回True；否则返回False。
        """
        start_time = time.time()
        while True:
            with self._initialized_lock:
                if self._initialized:
                    return True
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.1)


    def start(self) -> bool:
        """
        启动识别器，初始化摄像头与模型，并开启后台线程。
        
        Returns:
            bool: 如果成功启动返回 True，如果已经在运行则返回 False
        """
        # ✅ 防止重复启动（线程安全检查）
        if self._capture_thread is not None and self._capture_thread.is_alive():
            logger.warning("识别器已经在运行中，跳过重复启动")
            return False
        
        if not self._init_camera() or not self._init_model():
            logger.error("初始化失败")
            raise Exception("摄像头或模型初始化失败")
            # return False

        self._stop_event.clear()
        
        # 启动采集线程
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
        
        # 启动推理线程
        self._infer_thread = threading.Thread(target=self._infer_loop, daemon=True)
        self._infer_thread.start()

        # ✅ 不立即设置 _initialized = True
        # 等待推理线程完成模型预热后设置
        
        logger.info("识别器线程已启动，正在预热模型...")
        return True


    def stop(self) -> None:
        """
        停止识别器，终止后台线程。
        """
        self._stop_event.set()
        
        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=2.0)
        if self._infer_thread and self._infer_thread.is_alive():
            self._infer_thread.join(timeout=2.0)
        
        with self._initialized_lock:
            self._initialized = False
        
        logger.info("识别器已停止")


    def clean_up(self) -> None:
        """释放资源，关闭摄像头与窗口。"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()


    def get_latest_boxes(self) -> t.List[t.List[float]]:
        """
        获取最新的边界框列表。
        Returns:
            List[List[float]]: 最新的边界框列表，每个边界框格式为 [x1, y1, x2, y2]。
        """
        with self._lock:
            return list(self._latest_boxes)


    def _init_camera(self) -> bool:
        """初始化摄像头，设置分辨率与帧率。"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            logger.error("摄像头未打开")
            return False

        # 🔥 性能优化：启用硬件加速
        try:
            self.cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
        except:
            logger.warning("硬件加速设置失败（可能不支持）")
        
        # 🔥 优化：减少缓冲区延迟
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # 设置分辨率和帧率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.cam_fps)
        
        # 🔥 优化：使用 MJPEG 格式减少解码开销
        try:
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G')) # type: ignore
        except:
            logger.warning("MJPEG 格式设置失败")

        # 测试摄像头是否正常工作
        for i in range(10):
            ret, _ = self.cap.read()
        if not ret: # type: ignore
            logger.error("摄像头未读取到帧")
            self.cap.release()
            self.cap = None
            return False

        logger.info(f"摄像头初始化完成: {self.cam_width}x{self.cam_height}@{self.cam_fps}fps")
        return True


    def _init_model(self) -> bool:
        """初始化YOLO模型（ONNX Runtime 后端）。"""
        try:
            # 初始化模型
            logger.info(f"📦 正在加载 ONNX 模型: {self.model_path}")
            self.model = YOLO(self.model_path, task="detect")
            logger.info("✅ ONNX Runtime 后端已加载（CPU 优化）")
            
            # 使用虚拟图像预热
            dummy_frame = np.zeros((self.cam_height, self.cam_width, 3), dtype=np.uint8)
            logger.info("🔥 预热推理 (3次)...")
            for i in range(3):
                self.model.predict(dummy_frame, verbose=False)
            
            logger.info(f"✅ YOLO 模型已加载并预热完成")
            return True
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            logger.error("请确保已导出 ONNX 模型: python tools/export_onnx_optimized.py")
            self.model = None
            return False


    def _capture_loop(self) -> None:
        """采集线程：专注高频采集，直接将帧放入队列"""
        # 🔥 性能优化：绑定到 CPU 核心 0
        try:
            import os
            os.sched_setaffinity(0, {0}) # type: ignore
            logger.info("采集线程启动（绑定 CPU 0）")
        except Exception as e:
            logger.info(f"采集线程启动（CPU 绑定失败: {e}）")
        
        while not self._stop_event.is_set():
            if self.cap is None:
                time.sleep(0.01)
                continue
                
            ret, frame = self.cap.read()
            if ret:
                try:
                    # 如果队列满，丢弃旧帧
                    if self._frame_queue.full():
                        try:
                            self._frame_queue.get_nowait()
                        except queue.Empty:
                            pass
                    self._frame_queue.put_nowait(frame)
                except queue.Full:
                    pass  # 队列满时静默丢弃当前帧
            else:
                time.sleep(0.01)  # 采集失败时短暂休眠
        
        logger.info("采集线程退出")


    def _infer_loop(self) -> None:
        """
        推理线程：模型预热 + 智能跳帧策略 + 最大速度推理
        
        流程：
        1. 等待首帧用于预热
        2. 使用真实帧预热模型（3 次推理）
        3. 清空预热期间的旧帧
        4. 设置就绪标志
        5. 开始正常推理（智能跳帧 + 最大速度）
        """
        # 🔥 性能优化：绑定到 CPU 核心 2-3（性能核心）
        try:
            import os
            os.sched_setaffinity(0, {2, 3}) # type: ignore
            logger.info("推理线程启动（绑定 CPU 2-3）")
        except Exception as e:
            logger.info(f"推理线程启动（CPU 绑定失败: {e}）")
        
        # ============================================================
        # 阶段 1：模型预热（解决首次推理延迟问题）
        # ============================================================
        logger.info("等待首帧用于模型预热...")
        
        # 等待采集线程提供首帧
        warmup_frame = None
        while warmup_frame is None and not self._stop_event.is_set():
            try:
                warmup_frame = self._frame_queue.get(timeout=0.5)
            except queue.Empty:
                continue
        
        if warmup_frame is None:
            logger.error("未能获取预热帧，推理线程退出")
            return
        
        # 使用真实帧预热模型（3 次推理）
        logger.info("🔥 开始模型预热（首次推理需要 5-10 秒，请稍候）...")
        try:
            for i in range(3):
                self.model.predict(warmup_frame, conf=self.conf, iou=self.iou, verbose=False) # type: ignore
                logger.info(f"   预热进度: {i+1}/3")
            logger.info("✅ 模型预热完成！")
        except Exception as e:
            logger.error(f"❌ 模型预热失败: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 清空预热期间积累的旧帧
        cleared_frames = 0
        while not self._frame_queue.empty():
            try:
                self._frame_queue.get_nowait()
                cleared_frames += 1
            except queue.Empty:
                break
        logger.info(f"已清空预热期间的 {cleared_frames} 帧旧数据")
        
        # 设置就绪标志（wait_until_initialized 会返回）
        with self._initialized_lock:
            self._initialized = True
        
        # 记录推理开始时间（用于计算平均 FPS）
        self._inference_start_time = time.time()
        logger.info("🚀 识别器完全就绪，开始实时推理！")
        
        # ============================================================
        # 阶段 2：正常推理循环（智能跳帧 + 最大速度）
        # ============================================================
        
        while not self._stop_event.is_set():
            try:
                # 🔥 关键优化：清空队列，只取最新帧
                frame = None
                dropped_count = 0
                
                # 取出所有旧帧，只保留最新的
                while not self._frame_queue.empty():
                    try:
                        frame = self._frame_queue.get_nowait()
                        dropped_count += 1
                    except queue.Empty:
                        break
                
                # 至少丢弃一帧才算有效（因为我们取了最新帧）
                if dropped_count > 0:
                    dropped_count -= 1
                    self._dropped_frame_count += dropped_count
                
                # 如果有帧，立即进行推理（无延迟）
                if frame is not None:
                    self._process_frame(frame)
                    # 更新最后推理时间戳
                    self._last_inference_time = time.time()
                else:
                    # 队列为空时短暂休眠，避免空转浪费 CPU
                    time.sleep(0.001)  # 1ms 休眠
                    
            except Exception as e:
                logger.error(f"推理循环异常: {e}")
                time.sleep(0.01)
        
        logger.info("推理线程退出")


    def _process_frame(self, frame: cv2.typing.MatLike) -> None:
        """处理单帧：推理 + 生成注释帧 + 更新结果"""
        if self.model is None:
            return
            
        try:
            # 执行推理
            results = self.model.predict(
                source=frame,
                conf=self.conf,
                iou=self.iou,
                verbose=False  # 减少日志输出
            )
            
            # 生成带注释的帧用于显示
            if IF_ANNOTATE:
                self.current_annotated_frame = results[0].plot()

            # 提取边界框
            boxes = self._extract_boxes(results[0])
            # 线程安全地更新结果
            with self._lock:
                self._latest_boxes = boxes

            self._predict_frame_count += 1
                
        except Exception as e:
            logger.error(f"帧处理失败: {e}")


    def _extract_boxes(self, result) -> t.List[t.List[float]]:
        """从YOLO结果中提取边界框"""
        try:
            if result.boxes is None or len(result.boxes) == 0:
                return []
            return result.boxes.xyxy.cpu().numpy().tolist()
        except Exception as e:
            logger.error(f"边界框提取失败: {e}")
            return []


    def imshow(self, win_name: str = "Recognizer", wait: int = 1) -> None:
        """
        调试用：展示推理帧（带注释）或原始帧。
        """

        if not IF_IMSHOW:
            return

        # 优先显示推理帧，否则尝试获取队列中的原始帧
        if self.current_annotated_frame is not None:
            imshow_frame = cv2.resize(self.current_annotated_frame, (self.imshow_width, self.imshow_height))
            cv2.imshow(win_name, imshow_frame)
            cv2.waitKey(wait)
        elif not self._frame_queue.empty():
            try:
                frame = self._frame_queue.queue[0]  # 查看队列中的帧但不取出
                cv2.imshow(win_name, frame)
                cv2.waitKey(wait)
            except:
                logger.warning("无可显示帧")
        else:
            logger.warning("无可显示帧")
