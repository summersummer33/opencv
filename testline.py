import cv2
import numpy as np
import math
import time
import serial 
import testdef


frameWidth = 640
frameHeight = 480
cap = cv2.VideoCapture("/dev/up_video")
# cap=cv2.VideoCapture(2)
cap.set(3, frameWidth)
cap.set(4, frameHeight)
# cap.set(10,150)
cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
ser=testdef.serialInit()



while True:
    ret,frame = cap.read()
    ret,frame = cap.read()
    ret,frame = cap.read()
    cv2.imshow("frame",frame)
    theta,line_flag=testdef.detectLine(cap)
    # testdef.sendMessage4(ser,theta)
    print(theta)


    

