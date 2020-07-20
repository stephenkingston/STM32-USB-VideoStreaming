import cv2
import time

video2 = cv2.VideoCapture("D:\\SSD1306_VideoPlayer\\media\\sample.mp4")
_, frame = video2.read()
cv2.imshow("Image", frame)
cv2.waitKey(1000)