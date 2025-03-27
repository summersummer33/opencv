import cv2
import numpy as np
from pyzbar.pyzbar import decode
import testdef



frameWidth = 1280  #����ͼ����С
frameHeight = 720
cap = cv2.VideoCapture('/dev/code_video1',cv2.CAP_V4L2)
cap.set(3, frameWidth)
cap.set(4, frameHeight)
# cap.set(10,150)  #����ͼ������



# while True:
#     ret,frame = cap.read()
#     ret,frame = cap.read()
#     ret,frame = cap.read()
#     cv2.imshow("frame",frame)
    # barcodes = decode(frame)  
    # flag = 0
    # data = []
    # cv2.waitKey(10)

    
    # for barcode in barcodes:
    #     #rect = barcode.rect
    #     #x, y, w, h = rect
    #     #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  #��ʾ��ά���
    #     data = barcode.data.decode("utf8")
    #     print(data)
    #     #cv2.putText(frame, data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)  #��ʾ��ά������
    # if len(barcodes)>0:
    #     flag = 1

while True:
    data,code_flag = testdef.code(cap)  #处理二维码图像
    if(len(data) == 7 and code_flag == 1):
        break
print(data)
data1 = data[0:3]
data2 = data[4:7]
print("data1",data1)
print("data2",data2)