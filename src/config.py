# config.py
# 项目参数配置
#
# @author n1ghts4kura
# @date 25-12-5
#

# =============================
# 请仔细检阅所有参数！！！！
# =============================

# === 调试模式 ===
DEBUG_MODE  = True  # 是否启用调试模式，启用后会打印更多日志信息
IMSHOW_ON   = False # 是否显示OpenCV2窗口 (请在有显示器连接时启用)
ANNOTATE_ON = False # 是否在显示的图像上绘制标注 (如检测框、关键点等)

# === 摄像头参数配置 ===
CAMERA_INDEX         =     0   # 摄像头索引，默认0为内置摄像头
CAMERA_WIDTH         =   640   # 摄像头分辨率宽度
CAMERA_HEIGHT        =   480   # 摄像头分辨率高度
CAMERA_FPS           =    60   # 摄像头帧率
CAMERA_FOURCC        = "MJPG"  # 摄像头编码格式
CAMERA_AUTO_EXPOSURE =     1   # 自动曝光模式
CAMERA_EXPOSURE      =    64   # 曝光时间

# === 串口参数配置 ===
import serial as s
SERIAL_PORT          = "/dev/ttyUSB0"  # 串口设备路径
SERIAL_BAUDRATE      = 115200          # 串口波特率
SERIAL_TIMEOUT       = 4               # 串口**读取**超时时间（秒）
SERIAL_BYTESIZE      = s.EIGHTBITS     # 串口数据位
SERIAL_PARITY        = s.PARITY_NONE   # 串口校验位
SERIAL_STOPBITS      = s.STOPBITS_ONE  # 串口停止位
SERIAL_EOL           = "\n"            # 串口通信结束符
SERIAL_RX_DELAY      = 0.01            # 串口接收线程轮询延时（秒）
SERIAL_TX_DELAY      = 0.08

# === 自瞄模型相关配置 ===
AIMBOT_MODEL_PATH      = "model/aimbot/model.onnx"  # 自瞄模型路径
AIMBOT_PREDICT_DEVICE  = "CPU"                     # 自瞄模型推理设备 ("CPU" 或 "GPU")

# =================================

__all__ = [
    "DEBUG_MODE",
    "IMSHOW_ON",
    "ANNOTATE_ON",
    "CAMERA_INDEX",
    "CAMERA_WIDTH",
    "CAMERA_HEIGHT",
    "CAMERA_FPS",
]