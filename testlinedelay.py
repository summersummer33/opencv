import cv2
import threading
import numpy as np
import testdef



class Camera:

    def __init__(self, camera):
        self.frame = []
        self.ret = False
        self.cap = object
        self.camera = camera
        self.openflag = False

    def open(self):
        # if self.cap == object:
        self.cap = cv2.VideoCapture(self.camera,cv2.CAP_V4L2)
        # self.ret = self.cap.set(3, 320)
        # self.ret = self.cap.set(4, 240)
        self.ret = self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        self.ret = self.cap.set(cv2.CAP_PROP_EXPOSURE, float(0.6)) 
        self.ret = False
        self.openflag = True
        threading.Thread(target=self.queryframe, args=()).start()

    def queryframe(self):
        # self.openflag = True
        # while True:
        while self.openflag:
            self.ret, self.frame = self.cap.read()
            # pass

    def getframe(self):
        return self.ret, self.frame

    def close(self):
        self.openflag = False
        self.cap.release()



ser=testdef.serialInit()
camera = Camera(0)
camera.open()


while True:
    ret,image = camera.getframe()
    cv2.imshow('img',image)
    theta,line_flag=testdef.detectLine(camera)
    # testdef.sendMessage4(ser,theta)
    print(theta)

