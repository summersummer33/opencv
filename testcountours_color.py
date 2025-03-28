import cv2
import numpy as np
import math
import serial 



frameWidth = 1280
frameHeight = 720
color_cap = cv2.VideoCapture("/dev/up_video1",cv2.CAP_V4L2)
color_cap.set(3, frameWidth)
color_cap.set(4, frameHeight)
color_cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
color_cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
color_cap.set(cv2.CAP_PROP_EXPOSURE, float(0.2)) 

dim_red_min =   [  0, 60 ,60]
dim_red_max =   [ 12,203, 255]
dim_green_min = [30,48,54]# 60 60
dim_green_max = [78,234,255]
# dim_green_min = [61,48,54]# 30 48 54   61/48/54 61 taida    #zhuanpan   fanghuangse
# dim_green_max = [78,234,255]#78,234,255
dim_blue_min =  [82,105,0]#100 60 80
dim_blue_max =  [120,255,255]#124 230 255
dim_red_min1 =   [  160, 50 ,50]
dim_red_max1 =   [ 180,255, 255]
color_number=2

correct_x = 0
correct_y = 0


while True:
    flag_color_1 = 0
    red_min   =  np.array(dim_red_min)
    red_max   =  np.array(dim_red_max)
    green_min =  np.array(dim_green_min)
    green_max =  np.array(dim_green_max)
    blue_min  =  np.array(dim_blue_min)   
    blue_max  =  np.array(dim_blue_max)  
    red_min1   = np.array(dim_red_min1)  
    red_max1   = np.array(dim_red_max1)#��������ɫ��ֵ����ɫ��hsvɫ������h��С�Ĳ��ֺ�h�ܴ����������
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret,frame = color_cap.read()
    # print("ret:",ret)
    # corrected_frame=undistortion(frame,mtx,dist)
    

    src1 = frame.copy()
    res1 = src1.copy()
    hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV)    # ��BGRͼ��ת��ΪHSVͼ��
    mask12 = cv2.inRange(hsv,   red_min,   red_max)
    mask11 = cv2.inRange(hsv,   red_min1,   red_max1)
    mask2 = cv2.inRange(hsv, green_min, green_max)#�õ�������ɫ����ԭͼƬ���ɰ�
    mask3 = cv2.inRange(hsv,  blue_min,  blue_max)
    mask1 = cv2.add(mask12,mask11)
    if color_number == 1:
        mask0 = mask1
    elif color_number == 2:
        mask0 = mask2
    elif color_number == 3:
        mask0 = mask3
    res1 = cv2.bitwise_and(src1, src1, mask=mask0)   # Ӧ���ɰ�
    cv2.imshow("res1",res1)

    h, w = res1.shape[:2]
    blured = cv2.blur(res1, (7, 7))#�˲�
    blured = cv2.blur(res1, (5, 5))
    ret, bright = cv2.threshold(blured, 10, 255, cv2.THRESH_BINARY)#��ֵ��
    
    gray = cv2.cvtColor(bright, cv2.COLOR_BGR2GRAY)
    h_g, w_g = gray.shape[:2]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)#������
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)

    contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)#����������ڻ�ȡɫ�鷶Χ
    num = 0
    a_sum=0
    b_sum=0
    x_min = 4000
    x_max = 0
    y_min = 4000
    y_max = 0
    x_center = 0
    y_center = 0
    c = 0
    detx_p=0
    dety_p=0
    largest = None
    largest_area=0


    for contour in contours:
    # �������������
    # ���������С����
        area = cv2.contourArea(contour)
        # print("area:",area)
        if area > largest_area:
            largest_area = area
            largest=contour
    if largest is not None:
        (x1, y1, w1, h1) = cv2.boundingRect(largest)
        a = x1 + w1 / 2
        b = y1 + h1 / 2
        cv2.rectangle(src1, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2)  # ����⵽����ɫ������
        cv2.putText(src1, 'color', (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        area_text=f"{area}"
        cv2.putText(src1, area_text, (x1+60, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        center_text = f"({a}, {b})"
        cv2.putText(src1, center_text, (x1, y1+h1+5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        color_text=f"{color_number}"
        cv2.putText(src1, color_text, (x1, y1+h1+10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        flag_color_1 = 1
        detx_p = a - w/2 - correct_x
        dety_p = h/2 - correct_y - b
        detx_p = int(detx_p)
        dety_p = int(dety_p)
        print("detx:",detx_p,"dety:",dety_p)

    cv2.imshow("src1",src1)






    cv2.imshow("2",res1)
    





    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

