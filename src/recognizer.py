#
# recognizer.py
#
# @author n1ghts4kura
#

import cv2
import time
import queue
import threading
import numpy as np
import typing as t
from ultralytics import YOLO
from ultralytics.engine.results import Boxes

IF_IMSHOW = False # 是否显示窗口
IF_ANNOTATE = False # 是否生成带注释的帧（用于调试展示）

try:
    import src.logger as logger
    import src.config as config
except ImportError:
    import logger
    import config

class Recognizer:
    """
    视觉识别器

    主要接口:
    - get_instance(): 获取单例实例
    - start(): 启动识别器
    - stop(): 停止识别器
    - wait_until_initialized(): 阻塞等待初始化完成
    - is_running(): 检查识别器是否正在运行
    - get_latest_boxes(): 获取最新的边界框列表
    - get_status(): 获取识别器的详细运行状态
    """
    
    # 单例模式 实现
    _instance: t.Optional['Recognizer'] = None
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._instance_lock:
                # 双重检查锁定
                if cls._instance is None:
                    cls._instance = super(Recognizer, cls).__new__(cls)
        return cls._instance


    def __init__(
        self,
        cam_width: int = 480,
        cam_height: int = 320,
        imshow_width: int = 240,
        imshow_height: int = 160,
        cam_fps: float = 60.0,
        # target_inference_fps: int = 15,  # � 目标推理帧率（仅用于性能对比，不限制实际速度）
        # model_input_size: int = 320,      # 🔥 YOLO 输入尺寸（256/320/416）
    ) -> None:
        """
        Args:
            cam_width: 摄像头采集宽度
            cam_height: 摄像头采集高度
            imshow_width: 显示窗口宽度
            imshow_height: 显示窗口高度
            cam_fps: 摄像头帧率
            target_inference_fps: 目标推理帧率
            model_input_size: YOLO 输入尺寸
        """
        # 避免重复初始化（检查是否已有 cam_width 属性）
        if hasattr(self, 'cam_width'):
            return
        
        # 摄像头配置
        self.cam_width = cam_width
        self.cam_height = cam_height
        self.cam_fps = cam_fps

        # 推理配置
        # self.target_inference_fps = target_inference_fps  # � 目标推理帧率（用于性能对比）
        # self.model_input_size = model_input_size  # 🔥 YOLO 输入尺寸

        # 显示配置
        self.imshow_width = imshow_width
        self.imshow_height = imshow_height
        
        # 模型配置
        self.model_path = config.YOLO_MODEL_PATH
        self.conf: float = 0.3    # 置信度阈值
        self.iou: float = 0.7     # IOU 阈值
        self.device: str = "cpu"  # 推理设备（cpu / 0 / 1 等）
        
        # 运行状态
        self._initialized: bool = False
        
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
        
        # 状态锁：保护 _initialized 和 _latest_boxes
        self._state_lock = threading.Lock()
        
        # 结果存储
        self._latest_boxes: Boxes = Boxes(np.empty((0, 6)), orig_shape=(self.cam_height, self.cam_width))  # 初始化为空 Boxes 对象

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
        """
        if cls._instance is None:
            return cls(**kwargs)
        return cls._instance


    def _is_thread_alive(self, thread: t.Optional[threading.Thread]) -> bool:
        """
        检查采集/推理线程 是否存活且未停止。
        """

        return (
            thread is not None and 
            thread.is_alive() and 
            not self._stop_event.is_set()
        )

    
    def is_running(self) -> bool:
        """
        检查识别器是否正在运行（采集线程和推理线程都在活跃状态）。
        
        Returns:
            bool: 如果采集线程和推理线程都在运行，返回 True；否则返回 False。
        """

        # 检查初始化状态
        with self._state_lock:
            if not self._initialized:
                return False
        
        # 检查线程是否存活且未停止
        return (
            self._is_thread_alive(self._capture_thread) and 
            self._is_thread_alive(self._infer_thread)
        )

    
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
        """

        with self._state_lock:
            initialized = self._initialized
        
        capture_alive = self._is_thread_alive(self._capture_thread)
        infer_alive = self._is_thread_alive(self._infer_thread)
        
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
            with self._state_lock:
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
        # 防止重复启动
        if self._capture_thread is not None and self._capture_thread.is_alive():
            logger.warning("识别器已经在运行中，跳过重复启动")
            return False
        
        # 初始化摄像头与模型
        if not self._init_camera() or not self._init_model():
            logger.error("初始化失败")
            raise Exception("摄像头或模型初始化失败")
            # return False

        # 重置状态
        self._stop_event.clear()
        # 启动采集线程
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
        # 启动推理线程
        self._infer_thread = threading.Thread(target=self._infer_loop, daemon=True)
        self._infer_thread.start()

        logger.info("识别器启动中...")
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
        
        with self._state_lock:
            self._initialized = False
        
        logger.info("识别器已停止")


    def clean_up(self) -> None:
        """释放资源，关闭摄像头与窗口。"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()


    def get_latest_boxes(self) -> Boxes:
        """
        获取最新的边界框。
        Returns:
            Boxes: 最新的边界框对象
        """
        with self._state_lock:
            return self._latest_boxes


    def _init_camera(self) -> bool:
        """初始化摄像头，设置分辨率与帧率。"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            logger.error("摄像头未打开")
            return False

        # 性能优化：启用硬件加速
        try:
            self.cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
        except:
            pass  # 硬件加速不支持时静默忽略
        
        # 优化：减少缓冲区延迟
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # 设置分辨率和帧率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.cam_fps)
        
        # 优化：使用 MJPEG 格式减少解码开销
        try:
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G')) # type: ignore
        except:
            pass  # MJPEG 不支持时静默忽略

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
            self.model = YOLO(self.model_path, task="detect")
            
            # 使用虚拟图像预热
            dummy_frame = np.zeros((self.cam_height, self.cam_width, 3), dtype=np.uint8)
            for i in range(3):
                self.model.predict(dummy_frame, verbose=False)
            
            logger.info(f"模型加载完成: {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            logger.error("请确保已导出 ONNX 模型: python tools/export_onnx_optimized.py")
            self.model = None
            return False


    def _capture_loop(self) -> None:
        """采集线程：专注高频采集，直接将帧放入队列"""
        # 性能优化：绑定到 CPU 核心 0
        try:
            import os
            os.sched_setaffinity(0, {0}) # type: ignore
        except Exception:
            pass  # CPU 绑定失败时静默忽略
        
        while not self._stop_event.is_set():
            if self.cap is None:
                time.sleep(0.1)  # 摄像头未打开时休眠较长时间（100ms）
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
                time.sleep(0.1)  # 采集失败时休眠较长时间（100ms，异常情况）


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
        # 性能优化：绑定到 CPU 核心 2-3（性能核心）
        try:
            import os
            os.sched_setaffinity(0, {2, 3}) # type: ignore
        except Exception:
            pass  # CPU 绑定失败时静默忽略
        
        # ============================================================
        # 阶段 1：模型预热（解决首次推理延迟问题）
        # ============================================================
        
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
        logger.info("正在预热模型（首次需要 5-10 秒）...")
        try:
            for i in range(3):
                self.model.predict(warmup_frame, conf=self.conf, iou=self.iou, verbose=False) # type: ignore
        except Exception as e:
            logger.error(f"模型预热失败: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 清空预热期间积累的旧帧
        while not self._frame_queue.empty():
            try:
                self._frame_queue.get_nowait()
            except queue.Empty:
                break
        
        # 设置就绪标志（wait_until_initialized 会返回）
        with self._state_lock:
            self._initialized = True
        
        # 记录推理开始时间（用于计算平均 FPS）
        self._inference_start_time = time.time()
        logger.info("识别器就绪，开始推理")
        
        # ============================================================
        # 阶段 2：正常推理循环（智能跳帧 + 最大速度）
        # ============================================================
        
        while not self._stop_event.is_set():
            try:
                # 策略：完全非阻塞轮询（性能最佳）
                # 诊断测试显示：完全非阻塞能达到 4.02 FPS，空队列次数为 0
                # 说明推理速度跟得上采集速度，无需 sleep
                
                frame = None
                dropped_count = 0
                
                # 非阻塞地清空队列，只保留最新帧
                while not self._frame_queue.empty():
                    try:
                        frame = self._frame_queue.get_nowait()
                        dropped_count += 1
                    except queue.Empty:
                        break
                
                if frame is not None:
                    # 有帧，立即推理
                    if dropped_count > 0:
                        self._dropped_frame_count += (dropped_count - 1)
                    self._process_frame(frame)
                    self._last_inference_time = time.time()
                # else: 队列空时继续轮询（无 sleep）
                # 诊断显示空队列次数为 0，说明推理速度跟得上
                    
            except Exception as e:
                logger.error(f"推理循环异常: {e}")
                time.sleep(0.1)


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
            boxes = results[0].boxes
            if boxes is None:
                boxes = Boxes(np.empty((0, 6)), orig_shape=(self.cam_height, self.cam_width))
            boxes = boxes.cpu()
            # 线程安全地更新结果
            with self._state_lock:
                self._latest_boxes = boxes

            self._predict_frame_count += 1
                
        except Exception as e:
            logger.error(f"帧处理失败: {e}")



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
