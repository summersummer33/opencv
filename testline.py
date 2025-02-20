import cv2
import numpy as np
import math
import time
import serial 
import testdef
import threading





# #multi_threading
# # global cap
# class VideoCaptureThread:
#     def __init__(self, index=0):
#         self.cap = cv2.VideoCapture("/dev/up_video",cv2.CAP_V4L2)
#         self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
#         self.cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
#         # self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
#         self.frame = None
#         self.running = True
#         self.lock = threading.Lock()
#         self.thread = threading.Thread(target=self.update)
#         self.thread.start()

#     def update(self):
#         while self.running:
#             ret, frame = self.cap.read()
#             if ret:
#                 with self.lock:  # ȷ���̰߳�ȫ
#                     self.frame = frame

#     def read(self):
#         with self.lock:  # ȷ���̰߳�ȫ
#             return self.frame

#     def stop(self):
#         self.running = False
#         self.thread.join()
#         self.cap.release()


# # ʹ��ʾ��
# cap = VideoCaptureThread()


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
    # frame = cap.read()
    # if frame is not None:
    #     cv2.imshow('Frame', frame)
    #     # print("111111111")
    #     theta,line_flag=testdef.detectLine(frame)
    #     # testdef.sendMessage4(ser,theta)
    #     if line_flag ==0:
    #             testdef.sendMessage4(ser,theta)
    #             # print("main li de theta:",theta)
    #     elif line_flag==1:
    #             # print("line_flag:",line_flag)
    #         print("line okokokokokokokokok")
    #         testdef.sendMessage(ser,39)
    #         time.sleep(0.01)
    #         testdef.sendMessage(ser,40)
    # else:
    #     print("222222222")
    # ret,frame = cap.read()
    # ret,frame = cap.read()
    # ret,frame = cap.read()
    # cv2.imshow("frame",frame)
    theta,line_flag=testdef.detectLine(cap)
    testdef.sendMessage4(ser,theta)
    if line_flag ==0:
                testdef.sendMessage4(ser,theta)
                # print("main li de theta:",theta)
    elif line_flag==1:
                # print("line_flag:",line_flag)
            print("line okokokokokokokokok")
            # testdef.sendMessage(ser,39)
            # time.sleep(0.01)
            # testdef.sendMessage(ser,40)
    # print(theta)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    

