import cv2
import numpy as np
import math
import serial 



frameWidth = 640
frameHeight = 480
color_cap = cv2.VideoCapture("/dev/up_video",cv2.CAP_V4L2)
color_cap.set(3, frameWidth)
color_cap.set(4, frameHeight)
color_cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
# color_cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
# color_cap.set(cv2.CAP_PROP_EXPOSURE, float(0.2)) 

dim_red_min =   [  0, 60 ,60]
dim_red_max =   [ 12,203, 255]
dim_green_min = [30,48,54]# 60 60
dim_green_max = [78,234,255]
dim_blue_min =  [82,105,0]#100 60 80
dim_blue_max =  [120,255,255]#124 230 255
dim_red_min1 =   [  160, 50 ,50]
dim_red_max1 =   [ 180,255, 255]
color_number=3

correct_x = 42
correct_y = 16

dim_gray_min=[95,0,0]
dim_gray_max=[180,255,255]
                     

while True:
    flag_color_1 = 0


    gray_min = np.array(dim_gray_min)
    gray_max = np.array(dim_gray_max)

    ret = color_cap.grab()
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret,frame = color_cap.read()

    
    y0,x0 = frame.shape[:2]
    frame_change = cv2.resize(frame, (int(x0), int(y0)))

    src1 = frame_change.copy()
    res1 = src1.copy()
    hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV)    # ��BGRͼ��ת��ΪHSVͼ��
    mask_gray = cv2.inRange(hsv,   gray_min,   gray_max)

    res1 = cv2.bitwise_and(src1, src1, mask=mask_gray)   # Ӧ���ɰ�
    cv2.imshow("res1",res1)

    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   #ת�Ҷ�ͼ
    # equalized = cv2.equalizeHist(gray)
    # cv2.imshow("junheng",equalized)
    # ret, thresh = cv2.threshold(equalized, 120, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(res1, cv2.MORPH_CLOSE, kernel)#������
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    # closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)
    blurred = cv2.GaussianBlur(closed1, (9, 9), 2)
    edges = cv2.Canny(blurred, 50, 150)
    cv2.imshow("edges",edges)

    lines = cv2.HoughLines(edges,1,np.pi/180,threshold =150)#��ȡͼ�е���
    cnt = 0
    sumTheta = 0
    averageTheta = 0
    # global last_theta
    last_theta = 0
    if lines is not None:
        for line in lines:#��ÿ���߻�����
            rho,theta = line[0]
            
            if ((np.abs(theta)>=1.1) & (np.abs(theta)<=2.2)):#ȡ�Ƕ���һ�����ߣ���λ�ǻ��� #����ĽǶ��Ǹ��ߵĴ��ߵĽǶ�
                cnt = cnt + 1
                sumTheta = sumTheta + theta / 5.0
                # sumTheta = sumTheta + theta
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))
                cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),2)
    if not (cnt == 0):
        averageTheta = 5.0 * sumTheta / cnt #��ýǶȵ�ƽ��ֵ
        # averageTheta = sumTheta / cnt
        last_theta =  averageTheta
    else :
        averageTheta = last_theta
    # print(averageTheta)
    averageTheta180=np.degrees(averageTheta)
    finaltheta=90-averageTheta180
    print("hudu:",averageTheta,"   jiaodu:",averageTheta180,"    jiajiao;",finaltheta)
    cv2.imshow("line",frame)
    line_flag=0
    # if(abs(finaltheta)<0.8  and abs(finaltheta)>0.1):
    if abs(finaltheta)<0.5:
    # if abs(finaltheta)<1:
        line_flag=1
    # if finaltheta<-0.5 and finaltheta>-1.5:
    #     line_flag=1
    finaltheta=int(round(finaltheta))
    if (finaltheta==90 ):
        finaltheta=0
    cv2.waitKey(1)



    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

