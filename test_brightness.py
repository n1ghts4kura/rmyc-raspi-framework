import sys
import cv2
import time

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video device.")
    sys.exit()
time.sleep(2)  # Allow camera to warm up

brightness = cap.get(cv2.CAP_PROP_BRIGHTNESS)
print(f"Current brightness: {brightness}")
# _, frame = cap.read()
# cv2.imshow("Frame", cv2.resize(frame, (240, 240)))
# cv2.waitKey(0)

new_brightness = 0.5  # Set to a value between 0 and 1
cap.set(cv2.CAP_PROP_BRIGHTNESS, new_brightness)
time.sleep(1)  # Allow time for the setting to take effect
updated_brightness = cap.get(cv2.CAP_PROP_BRIGHTNESS)
print(f"Updated brightness: {updated_brightness}")
_, frame = cap.read()
cv2.imshow("Frame", frame)
cv2.waitKey(0)

time.sleep(10)
input()
