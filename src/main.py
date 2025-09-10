# main.py

from recognizer import Recognizer as R

a = R()

while not a.init_camera():
    print("摄像头初始化失败，正在重试...")

a.init_model()


while True:
    print(f"捕获帧: {a.capture()}")
    print(f"预测: {a.predict()}")
    print(f"标注并显示: {a.annotate()}")
    a.imshow()

input()
