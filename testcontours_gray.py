import cv2
import numpy as np
import math
import serial 
import time

correct_x = 0
correct_y = 0

frameWidth = 1280
frameHeight =720
cap = cv2.VideoCapture("/dev/up_video1")
# cap=cv2.VideoCapture(2)
cap.set(3, frameWidth)
cap.set(4, frameHeight)
# cap.set(10,150)
cap.set(cv2.CAP_PROP_BRIGHTNESS,10)

dim_red_min =   [  0, 60 ,60]
dim_red_max =   [ 12,203, 255]
dim_green_min = [45,60,60]# 60 60
dim_green_max = [95,250,250]
dim_blue_min =  [100,60,80]
dim_blue_max =  [124,230,255]
dim_red_min1 =   [  160, 50 ,50]
dim_red_max1 =   [ 180,255, 255]

# npzfile = np.load('calibrate.npz')
# mtx = npzfile['mtx']
# dist = npzfile['dist']
# def undistortion(img, mtx, dist):   #jibian 
#     h, w = img.shape[:2]
#     newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

#     # print('roi ', roi)

#     dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

#     # crop the image
#     x, y, w, h = roi
#     if roi != (0, 0, 0, 0):
#         dst = dst[y:y + h, x:x + w]

#     return dst

while True:
    time1=time.time()
    success, frame = cap.read()
    # cv2.imshow("origin",frame)
    src1 = frame.copy()
    res1 = src1.copy()
    h, w = res1.shape[:2]


    gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)   #ת�Ҷ�ͼ
    equalized = cv2.equalizeHist(gray)
    # cv2.imshow("junheng",equalized)
    blurred = cv2.GaussianBlur(equalized, (9, 9), 2)
    edges = cv2.Canny(blurred, 50, 150)
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 0.7,70,
                            param1=100, param2=150, minRadius=50, maxRadius=0)    #ʶ��Բ��
    flag = 0
    detx = 0 #�����Ĳ��
    dety = 0
    detx1=0
    dety1=0

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)
    edges1 = cv2.Canny(blurred, 50, 150)
    # cv2.imshow("blu",blurred)
    cv2.imshow("edges1",edges1)
    contours, _ = cv2.findContours(edges1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# ��ʼ������
    largest_circle = None
    largest_area = 0

    move_flag = 0
    stop_flag = 0


    for contour in contours:
    # �������������
    # ���������С����
        area = cv2.contourArea(contour)
        # print("area:",area)
        if area > largest_area:
            largest_area = area
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            if len(approx) > 7:  # Բ�εĽ��ƶ���α���Ӧ�ô���8
                largest_circle = approx
                # print("largest area:",largest_area)
                if largest_area > 10000 :
                    cv2.drawContours(res1, [largest_circle], 0, (0, 0, 255), 3)
                    # ����Բ�ĺͰ뾶
                    (x, y), radius = cv2.minEnclosingCircle(largest_circle)
                    # print("x=",x,"y=",y)
                    center = (int(x), int(y))
                    radius = int(radius)
                    detx = x - w/2 - correct_x
                    dety = h/2 - correct_y - y
                    print("detx=",detx,"dety=",dety)
                    detx1 = int(round(detx))
                    dety1 = int(round(dety))
                    cv2.circle(res1, center, 2, (0, 0, 255), 3)
                    # ����Բ
                    cv2.circle(res1, center, radius, (0, 255, 0), 2)
                    center_text = f"({center[0]}, {center[1]}), radius: {radius}"
                    text_position = (center[0] + 10, center[1] - 10)
                    area_text=f"({largest_area})"
                    cv2.putText(res1, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                    cv2.putText(res1, area_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    print('  detx1:',detx1,'  dety1:',dety1)


                else:
                    cv2.putText(res1, 'no', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    # print("no")
                    # ser.write(b'no circle')
    if abs(detx)<3.5 and abs(dety)<3.5:
        if abs(detx)!= 0 or abs(detx)!= 0:
            stop_flag = 1
    cv2.imshow("res1",res1)
    # print(time.time()-time1)
    frame=None
    cv2.waitKey(1)