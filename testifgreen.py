import cv2
import numpy as np
import math
import time
import serial 
import testdef
import threading


frameWidth = 640
frameHeight = 480
cap = cv2.VideoCapture("/dev/up_video")
# cap=cv2.VideoCapture(2)
cap.set(3, frameWidth)
cap.set(4, frameHeight)
# cap.set(10,150)
cap.set(cv2.CAP_PROP_BRIGHTNESS,10)


while True:
    theta,line_flag,detx,dety,move_flag=testdef.together_line_circle1(cap)
    # testdef.sendMessage4(ser,theta)
    # if line_flag ==0:
    #             testdef.sendMessage4(ser,theta)
    #             # print("main li de theta:",theta)
    # elif line_flag==1:
    #             # print("line_flag:",line_flag)
    #         print("line okokokokokokokokok")
    #         # testdef.sendMessage(ser,39)S
    #         # time.sleep(0.01)
    #         # testdef.sendMessage(ser,40)
    # # print(theta)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break