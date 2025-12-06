"""
数据采集相关路由：MJPEG 预览 + 保存当前帧。
复用 vision.camera.Camera 单例，不依赖桌面环境。
"""

from __future__ import annotations

import threading
import time
from pathlib import Path

import cv2
from flask import Blueprint, Response, jsonify, send_from_directory

from src.vision.camera import Camera
from src import config


bp = Blueprint(
	"collector",
	__name__,
	url_prefix="/collector",
)


# 路径配置
STATIC_DIR = Path(__file__).parent / "data_collector"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CAPTURE_DIR = PROJECT_ROOT / "captured_pics"
CAPTURE_DIR.mkdir(parents=True, exist_ok=True)


# 采集线程共享状态
camera = Camera()
latest_frame: cv2.typing.MatLike | None = None
latest_jpeg: bytes | None = None
frame_lock = threading.Lock()
capture_thread: threading.Thread | None = None
capture_running = False
new_frame_event = threading.Event()


def _ensure_camera_thread() -> None:
	"""懒启动采集线程。"""
	global capture_thread, capture_running
	if capture_thread and capture_thread.is_alive():
		return

	capture_running = True
	capture_thread = threading.Thread(target=_capture_loop, daemon=True)
	capture_thread.start()


def _capture_loop() -> None:
	"""循环采集帧并缓存最新 JPEG。"""
	global latest_frame, latest_jpeg, capture_running

	if not camera.open():
		capture_running = False
		return

	interval = 1.0 / max(config.CAMERA_FPS, 1)

	while capture_running:
		ok, frame = camera.read()
		if ok and frame is not None:
			# 轻量编码 JPEG，降低 CPU 占用
			ret, buf = cv2.imencode(
				".jpg",
				frame,
				[
					cv2.IMWRITE_JPEG_QUALITY,
					70,
					cv2.IMWRITE_JPEG_OPTIMIZE,
					1,
				],
			)
			if ret:
				with frame_lock:
					latest_frame = frame
					latest_jpeg = buf.tobytes()
				new_frame_event.set()
		time.sleep(interval)

	camera.close()


def _mjpeg_generator():
	"""生成 MJPEG 流。"""
	while True:
		# 等待新帧，避免忙轮询
		new_frame_event.wait(timeout=0.5)
		new_frame_event.clear()
		with frame_lock:
			buf = latest_jpeg
		if buf:
			yield (
				b"--frame\r\n"
				b"Content-Type: image/jpeg\r\n"
				+ b"Content-Length: " + str(len(buf)).encode() + b"\r\n\r\n"
				+ buf
				+ b"\r\n"
			)
		else:
			time.sleep(0.01)


@bp.route("/page")
def page() -> Response:
	"""返回前端页面。"""
	return send_from_directory(STATIC_DIR, "page.html")


@bp.route("")
@bp.route("/")
def alias_root() -> Response:
	"""默认入口，等同 /collector/page。"""
	return send_from_directory(STATIC_DIR, "page.html")


@bp.route("/page.css")
def page_css() -> Response:
	"""返回页面样式。"""
	return send_from_directory(STATIC_DIR, "page.css")


@bp.route("/stream")
def stream() -> Response:
	"""MJPEG 流预览。"""
	_ensure_camera_thread()
	return Response(_mjpeg_generator(), mimetype="multipart/x-mixed-replace; boundary=frame")


@bp.route("/capture", methods=["POST"])
def capture():
	"""保存当前帧到服务器本地。"""
	with frame_lock:
		frame = None if latest_frame is None else latest_frame.copy()
		jpeg_bytes = None if latest_jpeg is None else bytes(latest_jpeg)

	if frame is None and jpeg_bytes is None:
		return jsonify({"ok": False, "error": "暂无帧数据"}), 503

	# 文件名需避免同一秒覆盖，使用微秒级时间戳
	filename = time.strftime("photo_%y%m%d_%H%M%S_", time.localtime()) + f"{int(time.time()*1_000_000) % 1_000_000:06d}.jpg"
	filepath = CAPTURE_DIR / filename

	ok = False
	if jpeg_bytes is not None:
		try:
			filepath.write_bytes(jpeg_bytes)
			ok = True
		except Exception:
			ok = False

	if not ok:
		# 回退到重新编码原帧
		ok = cv2.imwrite(str(filepath), frame) if frame is not None else False
	if not ok:
		return jsonify({"ok": False, "error": "保存失败"}), 500

	return jsonify({"ok": True, "file": f"/collector/captures/{filename}"})


@bp.route("/capture-count")
def capture_count() -> Response:
	"""返回已保存图片数量与文件列表。"""
	files = sorted((p.name for p in CAPTURE_DIR.glob("*.jpg")), reverse=True)
	return jsonify({"count": len(files), "files": files})


@bp.route("/captures/<path:fname>")
def serve_capture(fname: str) -> Response:
	"""访问已保存的帧文件。"""
	return send_from_directory(CAPTURE_DIR, fname)


@bp.route("/info")
def info() -> Response:
	"""摄像头状态调试信息。"""
	status = str(camera)
	return jsonify({"status": status})


__all__ = ["bp"]