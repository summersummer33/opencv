import cv2
import numpy as np
import math
import serial 

correct_x=36
correct_y=12



frameWidth = 640
frameHeight = 480
cap = cv2.VideoCapture("/dev/up_video1")
# cap=cv2.VideoCapture(2)
cap.set(3, frameWidth)
cap.set(4, frameHeight)
# cap.set(10,150)
cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
cap.set(cv2.CAP_PROP_EXPOSURE, float(0.1)) 


dim_red_min =   [  0, 133,68]
dim_red_max =   [ 11,255, 255]
dim_green_min = [44,51,0]# 60 60
dim_green_max = [67,255,255]
dim_blue_min =  [101,84,44] 
dim_blue_max =  [137,255,255]

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
    # success, frame = cap.read()
    # success, frame = cap.read()
    success=cap.grab()
    success=cap.grab()
    success=cap.grab()
    success, frame = cap.read()
    # corrected_frame=undistortion(frame,mtx,dist)
    # cv2.imshow("corrected",corrected_frame)
    cv2.imshow("frame",frame)
    src1 = frame.copy()
    res1 = src1.copy()
    # gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)   #ת�Ҷ�ͼ
    # blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    # edges = cv2.Canny(blurred, 50, 150)
    flag = 0
    detx = 0 #�����Ĳ��
    dety = 0
    h, w = res1.shape[:2]    

#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
#     opened = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)
#     closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
#     closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)
#     edges1 = cv2.Canny(blurred, 50, 150)
#     # cv2.imshow("closed",closed)
#     # cv2.imshow("edges1",edges1)

#     ret, thresh = cv2.threshold(closed, 200, 255, cv2.THRESH_BINARY_INV)

# # ��ʾͼ��
#     # cv2.imshow('Threshold', thresh)
#     adaptive_thresh = cv2.adaptiveThreshold(closed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                                        cv2.THRESH_BINARY, 11, 2)

# # ��ʾͼ��
#     edgead=cv2.Canny(adaptive_thresh,50,200)
#     # cv2.imshow('Adaptive Threshold', adaptive_thresh)
#     cv2.imshow('adedge',edgead)
#     # cv2.imshow('edges',edges)
#     cv2.imshow('edges1',edges1)
#     # cv2.imshow('gray',gray)
    gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)   #ת�Ҷ�ͼ
    equalized = cv2.equalizeHist(gray)
    # cv2.imshow("junheng",equalized)
    blurred = cv2.GaussianBlur(equalized, (9, 9), 2)
    edges = cv2.Canny(blurred, 50, 150)
    cv2.imshow('edges',edges)
    

    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 0.7,70,
                            param1=100, param2=65, minRadius=140, maxRadius=155)    #ʶ��Բ��
    # circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 0.7,70,
    #                         param1=100, param2=45, minRadius=160, maxRadius=190)    #ʶ��Բ�
    #124 155
    flag = 0
    detx = 0 #�����Ĳ��
    dety = 0
    detx1 = 0
    dety1 = 0
    largest_circle = None  # ���ڴ洢���Բ����Ϣ
    stop_flag=0
    if circles is not None:
        flag = 1
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
        # ����Ƿ�������Բ
            if largest_circle is None or i[2] > largest_circle[2]:
                largest_circle = i  # �������Բ����Ϣ

    # ����ҵ�������Բ�����Ƴ���
        if largest_circle is not None:
        # ������Բ
            cv2.circle(res1, (largest_circle[0], largest_circle[1]), largest_circle[2], (0, 0, 255), 2)
        # �������ĵ�
            cv2.circle(res1, (largest_circle[0], largest_circle[1]), 2, (0, 0, 255), 3)
            center_text = f"({largest_circle[0]}, {largest_circle[1]})"
        # �����ı�λ�ã�ͨ����Բ���Ϸ�
            text_position = (largest_circle[0] + 10, largest_circle[1] - 10)
        # ��ͼ���ϻ���Բ������
            cv2.putText(edges, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            radius = largest_circle[2]
            radius_text = f"Radius: {radius}"
            radius_position = (largest_circle[0] + 10, largest_circle[1] + 20)  # ѡ��һ�����ʵ�λ������ʾ�뾶��Ϣ
            cv2.putText(res1, radius_text, radius_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            detx = largest_circle[0] - w/2 -correct_x
            dety = h/2 - largest_circle[1] -correct_y
            detx1 = int(round(detx))
            dety1 = int(round(dety))
            print("detx=",detx,"dety=",dety)
            print("detx1=",detx1,"dety1=",dety1)
            # pi=math.pi
            # area=largest_circle[2]*largest_circle[2]*pi
            # area_text=f"{area}"
            # cv2.putText(res1, area_text, (largest_circle[0], largest_circle[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        cv2.putText(res1, 'no', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    # print(detx,dety)
    cv2.imshow("2",res1)
    if abs(detx)<4 and abs(dety)<4:
        if abs(detx)!= 0 or abs(detx)!= 0:
            stop_flag = 1


    cv2.waitKey(1)