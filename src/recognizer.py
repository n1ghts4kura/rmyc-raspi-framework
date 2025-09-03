
# recognizer.py
#
# @author **Aunnno**, n1ghts4kura
# @date 2025-09-03
#

import os, cv2
from ultralytics import YOLO

class recognizer:
    def __init__(self) -> None:
        self.photos_path = "photos" #图片路径
        self.model_path = "model" #模型路径
        self.cap_running = False
        self.model_running = False
        self.conf = 0.7 #置信度阈值
        self.iou = 0.7 #非极大值抑制
        if not os.path.exists(self.photos_path): #照片路径检测
            os.makedirs(self.photos_path)
        if not os.path.exists(self.model_path): #模型路径检测
            os.makedirs(self.model_path)
    def camera_init(self) -> bool: #摄像头初始化
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("未读取到摄像头")
                return False
            #摄像头参数设置
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480) #高480
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,640) #宽640
            self.cap.set(cv2.CAP_PROP_FPS,30.0) #帧率30
            self.cap_running = True
            print("摄像头打开成功")
            return True
        except Exception as e:
            print(f"摄像头打开出错:{e}")
            return False
    def model_init(self) -> bool: #模型初始化
        print("输入模型名:")
        name = input()
        path = os.path.join(self.photos_path,name)
        if not os.path.exists(path):
            print("未找到该文件")
        try:
            self.model = YOLO(path)
            if self.model is None:
                print("模型打开失败")
            self.model_running = True
            return True
        except Exception as e:
            print(f"打开模型时出现错误:{e}")
            return False
    def cap_to_display(self): #从摄像头获取图像，标注后显示到屏幕
        print("从摄像头到屏幕")
        print("按c结束")
        if not self.model_running:
            if not self.model_init():
                return
        if not self.cap_running:
            if not self.camera_init():
                return
        try:
            while True:
                ret,frame = self.cap.read()
                if not ret:
                    print("未读取到帧")
                    return
                results = self.model(frame,conf=self.conf,iou=self.iou,stream=True)
                out_frame = results[0].plot()
                cv2.imshow("camera",out_frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('c'):
                    return
        except Exception as e:
            print(f"实时检测错误:{e}")
    def photo_to_display(self): #获取照片，标注后显示到屏幕
        print("从照片到屏幕")
        print("按p结束")
        print("输入照片名:")
        name = input()
        path = os.path.join(self.photos_path,name)
        if not os.path.exists(path):
            print("未找到该文件")
            return
        if not self.model_running:
            if not self.model_init():
                return
        if not self.cap_running:
            if not self.camera_init():
                return
        try:
            while True:
                results = self.model(path,conf=self.conf,iou=self.iou)
                out_frame = results[0].plot()
                cv2.imshow("photo",out_frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('p'):
                    return
        except Exception as e:
            print(f"图片检测错误:{e}")
    def cap_to_robot(self): #从摄像头获取图像并返回中心点给车子
        if not self.model_running:
            if not self.model_init():
                return
        if not self.cap_running:
            if not self.camera_init():
                return
        try:
            while True:
                ret,frame = self.cap.read()
                if not ret:
                    print("未读取到帧")
                    return
                results = self.model(frame)
                boxes = results[0].boxes
                for i,box in enumerate(boxes):
                    x1,y1,x2,y2=box.xyxy[0].cpu().numpy()
                    x=(x1+x2)/2
                    y=(y1+y2)/2
                    #这里要写一个传数据的函数但是暂时没有
                key = cv2.waitKey(1) & 0xFF
                if key == ord('c'):
                    return
        except Exception as e:
            print(f"实时检测错误:{e}")
    def clean_up(self): #手动调用清理的接口
        if self.cap_running and self.cap is not None:
            self.cap_running = False
            self.cap.release()
        self.model_running = False
        cv2.destroyAllWindows()
    def __del__(self):
        self.clean_up() #嘻嘻，也直接调用clean_up