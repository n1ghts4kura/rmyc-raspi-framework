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
import logging
from ultralytics import YOLO

IF_PLOT = False

# 初始化日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Recognizer:
    """
    单摄像头、单模型识别器，支持后台线程持续抓帧与推理。
    采用双线程设计：采集线程专注高频采集，推理线程处理最新帧。
    用法：
        with Recognizer() as recog:
            recog.wait_until_initialized()
            # 在后台运行，其他线程可随时调用 get_latest_boxes()
            boxes = recog.get_latest_boxes()
    """

    def __init__(
        self,
        cam_width: int = 480,
        cam_height: int = 320,
        imshow_width: int = 160,
        imshow_height: int = 120,
        cam_fps: float = 60.0,
    ) -> None:
        # 摄像头配置
        self.cam_width = cam_width
        self.cam_height = cam_height
        self.cam_fps = cam_fps

        # 显示配置
        self.imshow_width = imshow_width
        self.imshow_height = imshow_height
        
        # 模型配置
        self.model_path: str = os.getenv("MODEL_PATH", "./model/yolov8n.pt")
        self.conf: float = 0.3  # 降低置信度阈值
        self.iou: float = 0.7
        
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

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
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
        """
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

        with self._initialized_lock:
            self._initialized = True
        
        logger.info("识别器启动完成")
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

        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
        self.cap.set(cv2.CAP_PROP_FPS, self.cam_fps)

        # Camera settings optimization 
        # self.cap.set(cv2.CAP)

        # 测试摄像头是否正常工作
        for i in range(10):
            ret, _ = self.cap.read()
        if not ret:
            logger.error("摄像头未读取到帧")
            self.cap.release()
            self.cap = None
            return False

        logger.info(f"摄像头初始化完成: {self.cam_width}x{self.cam_height}@{self.cam_fps}fps")
        return True

    def _init_model(self) -> bool:
        """初始化YOLO模型。"""
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"YOLO模型加载完成: {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            self.model = None
            return False

    def _capture_loop(self) -> None:
        """采集线程：专注高频采集，直接将帧放入队列"""
        logger.info("采集线程启动")
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
        """推理线程：从队列取帧进行推理"""
        logger.info("推理线程启动")
        while not self._stop_event.is_set():
            try:
                frame = self._frame_queue.get(timeout=1.0)
                self._process_frame(frame)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"推理循环异常: {e}")
        
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
            self.current_annotated_frame = results[0].plot()
            
            # 提取边界框
            boxes = self._extract_boxes(results[0])
            
            # 线程安全地更新结果
            with self._lock:
                self._latest_boxes = boxes
                
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

    def get_fps_info(self) -> dict:
        """获取性能信息（可选的调试功能）"""
        return {
            "queue_size": self._frame_queue.qsize(),
            "max_queue_size": self._frame_queue.maxsize,
            "initialized": self._initialized,
            "latest_boxes_count": len(self._latest_boxes)
        }
