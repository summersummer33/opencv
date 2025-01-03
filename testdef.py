import cv2
import numpy as np
import math
import time
import serial 
from pyzbar.pyzbar import decode  #ɨ��ά��Ŀ�


#��ɫ��ֵ
dim_red_min =   [  0, 60 ,60]
dim_red_max =   [ 12,203, 255]
dim_green_min = [45,60,60]# 60 60
dim_green_max = [95,250,250]
dim_blue_min =  [100,60,80]
dim_blue_max =  [124,230,255]
dim_red_min1 =   [  160, 50 ,50]
dim_red_max1 =   [ 180,255, 255]



# x=40 y=34  zai gao de shi hou wangyoul x+,wangxial y-
# 41 -20
correct_x=42
correct_y=16

npzfile = np.load('calibrate.npz')
mtx = npzfile['mtx']
dist = npzfile['dist']


def serialInit():#��ʼ������
    Pi_serial  =  serial.Serial( port="/dev/ttyAMA2",
                              baudrate=115200,
                              bytesize=serial.EIGHTBITS,
                              parity=serial.PARITY_NONE,
                              stopbits=serial.STOPBITS_ONE,
                              )
    return Pi_serial
    
def receiveMessage(ser):#������Ϣ
    count = ser.inWaiting()
    if count != 0:
            # ��ȡ���ݲ�����
        recv = ser.read(count)  #��ݮ�ɴ��ڽ�������
        # recv_data=recv.hex()
        recv_data=recv
        # if recv[0] == 0xAA and recv[1] == 0xBB and recv[-1] == 0xCC:
        #     # ��ȡ��һ��������
        #     recv_useful = recv[2]  # ��һ������������ڿ�ʼ��־֮��
        #     recv_data=recv_useful.hex()
        # else:
        #     recv_data = None  
    else:
        recv_data = None
    ser.flushInput()
    time.sleep(0.1)
    return recv_data

def sendMessage(ser,data):  
    data_hex=hex(data)[2:]
    data_hex = data_hex.zfill(2)
    # print(data_hex)
    # data_pack = 'AA'+'BB'+data_hex+'CC'
    # data_pack =data_hex
    # ser.write(bytes.fromhex(data))
    ser.write(bytes.fromhex(data_hex))
    print(data)
    time.sleep(1)

    # data_array = [0xAA,0xBB,data_hex,0xCC]
    # byte_array = bytearray(data_array)   
    # ser.write(byte_array) 

    return 0

def sendMessage2(ser,data1,data2):   #yuanhuan center
    if data1>0:
        signal1=1
    else :
        signal1=2
        data1=abs(data1)
        if data1>254:
            data1=254
    if data2>0:
        signal2=1
    else:
        signal2=2
        data2=abs(data2)
        if data2>254:
            data2=254
    data_hex1=hex(data1)[2:]
    data_hex1 = data_hex1.zfill(2)
    data_hex2=hex(data2)[2:]
    data_hex2 = data_hex2.zfill(2)
    signal_hex1=hex(signal1)[2:]
    signal_hex1 = signal_hex1.zfill(2)
    signal_hex2=hex(signal2)[2:]
    signal_hex2 = signal_hex2.zfill(2)
    # print(data_hex)
    data_pack = signal_hex1+data_hex1+signal_hex2+data_hex2
    # data_pack =data_hex
    # ser.write(bytes.fromhex(data))
    ser.write(bytes.fromhex(data_pack))
    print(data_pack)
    time.sleep(0.1)

    return 0


def sendMessage3(ser, data):    #code order
    if isinstance(data, list):
        length = len(data)
        # processed_data = []
        combined_data_hex=''
        for item in data:
            data_hex = hex(item)[2:]
            data_hex = data_hex.zfill(2)
            # processed_data.append(data_hex)
            combined_data_hex += data_hex

        combined_data_hex='09'+'09'+combined_data_hex
        print(f"Array length: {length}")
        # combined_data_hex = '+'.join(processed_data)
        # print(combined_data_hex)
        ser.write(bytes.fromhex(combined_data_hex))
        print(combined_data_hex)
        # print(combined_data_hex)
    else:
        data_hex = hex(data)[2:]
        data_hex = data_hex.zfill(2)
        ser.write(bytes.fromhex(data_hex))
        print(f"Single data: {data}")

def sendMessage4(ser,data1):   #line detect
    if data1>0:
        signal1=1
    else :
        signal1=2
        data1=abs(data1)
    # if data2>0:
    #     signal2=1
    # else:
    #     signal2=2
    #     data2=abs(data2)
    data_hex1=hex(data1)[2:]
    data_hex1 = data_hex1.zfill(2)
    # data_hex2=hex(data2)[2:]
    # data_hex2 = data_hex2.zfill(2)
    signal_hex1=hex(signal1)[2:]
    signal_hex1 = signal_hex1.zfill(2)
    # signal_hex2=hex(signal2)[2:]
    # signal_hex2 = signal_hex2.zfill(2)
    # print(data_hex)
    # data_pack = signal_hex1+data_hex1+signal_hex2+data_hex2
    # data_pack =data_hex
    # ser.write(bytes.fromhex(data))
    data_pack = signal_hex1+data_hex1
    ser.write(bytes.fromhex(data_pack))
    # print("angle direction:",data_pack)
    time.sleep(0.1)

    return 0

rec_detx=[]
rec_dety=[]
rec_detx1=[]
rec_dety1=[]
def findCountours(camera_cap): #ʶ��Բ��  ���ζ�λ
    success, frame = camera_cap.read()
    # frame = None
    success, frame = camera_cap.read()
    success, frame = camera_cap.read()
    success, frame = camera_cap.read()
    # success, frame = camera_cap.read()
    # cv2.imshow("origin",frame)

    corrected_frame=undistortion(frame,mtx,dist)
    src1 = corrected_frame.copy()
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
                    # cv2.drawContours(res1, [largest_circle], 0, (0, 0, 255), 3)
                    # ����Բ�ĺͰ뾶
                    (x, y), radius = cv2.minEnclosingCircle(largest_circle)
                    print("x=",x,"y=",y)
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

                    # 
                    # rec_detx1=rec_detx[1:2]
                    # rec_detx1.append(detx)
                    # rec_detx = rec_detx1

                    # if detx>0 and dety>0:
                    #     move_flag = 3
                    #     # ser.write(b'3')
                    # elif detx>0 and dety<0:
                    #     move_flag = 1
                    #     # ser.write(b'2')
                    # elif detx<0 and dety>0:
                    #     move_flag = 4
                    #     # ser.write(b'4')
                    # elif detx<0 and dety<0:
                    #     move_flag = 2
                        # ser.write(b'1')
                    # move_flag = hex(move_flag)
                    # move_byte=move_flag.to_bytes(4,'')
                    # ser.write(b'')
                else:
                    cv2.putText(res1, 'no', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    # print("no")
                    # ser.write(b'no circle')
    if abs(detx)<3.5 and abs(dety)<3.5:
        if abs(detx)!= 0 or abs(detx)!= 0:
            stop_flag = 1
    cv2.imshow("res1",res1)
    frame=None
    cv2.waitKey(1)
    return detx1,dety1,move_flag,stop_flag


def circlePut_meiyong(cap):  #�meiyong
    success, frame = cap.read()
    color_number =2   #ѡ��Ҫʶ�����ɫ  1��2��3��
    cv2.imshow("origin",frame)
    # cv2.imshow("Result", img)
    red_min   =  np.array(dim_red_min)   #ת��Ϊ����
    red_max   =  np.array(dim_red_max)
    green_min =  np.array(dim_green_min)
    green_max =  np.array(dim_green_max)
    blue_min  =  np.array(dim_blue_min)   
    blue_max  =  np.array(dim_blue_max)  
    red_min1   = np.array(dim_red_min1)  
    red_max1   = np.array(dim_red_max1)
    src1 = frame.copy()
    res1 = src1.copy()
    h, w = res1.shape[:2]
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
    gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)   #ת�Ҷ�ͼ
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    edges = cv2.Canny(blurred, 50, 150)
    # cv2.imshow("edge",edges)
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 0.7,70,
                            param1=100, param2=70, minRadius=50, maxRadius=0)    #ʶ��Բ��
    flag = 0
    detx = 0 #�����Ĳ��
    dety = 0
    largest_circle = None  # ���ڴ洢���Բ����Ϣ

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
            cv2.circle(res1, (largest_circle[0], largest_circle[1]), largest_circle[2], (0, 0, 255), 3)
        # �������ĵ�
            cv2.circle(res1, (largest_circle[0], largest_circle[1]), 2, (0, 0, 255), 3)
            center_text = f"({largest_circle[0]}, {largest_circle[1]})"
        # �����ı�λ�ã�ͨ����Բ���Ϸ�
            text_position = (largest_circle[0] + 10, largest_circle[1] - 10)
        # ��ͼ���ϻ���Բ������
            cv2.putText(edges, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            detx = largest_circle[0] - w/2 -correct_x
            dety = h/2 - largest_circle[1] -correct_y
    else:
        cv2.putText(res1, 'no', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imshow("2",edges)
    if abs(detx)<4 and abs(dety)<4:
        if abs(detx)!= 0 or abs(detx)!= 0:
            stop_flag = 1
    return detx,dety,stop_flag


def circlePut1(cap):
    success, frame = cap.read()
    success, frame = cap.read()
    success, frame = cap.read()
    corrected_frame=undistortion(frame,mtx,dist)
    cv2.imshow("corrected",corrected_frame)
    src1 = corrected_frame.copy()
    res1 = src1.copy()
    gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)   #ת�Ҷ�ͼ
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    edges = cv2.Canny(blurred, 50, 150)
    flag = 0
    detx = 0 #�����Ĳ��
    dety = 0
    h, w = res1.shape[:2]    

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)
    edges1 = cv2.Canny(blurred, 50, 150)
    # cv2.imshow("closed",closed)
    # cv2.imshow("edges1",edges1)

    ret, thresh = cv2.threshold(closed, 200, 255, cv2.THRESH_BINARY_INV)

# ��ʾͼ��
    # cv2.imshow('Threshold', thresh)
    adaptive_thresh = cv2.adaptiveThreshold(closed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)

# ��ʾͼ��
    edgead=cv2.Canny(adaptive_thresh,50,200)
    # cv2.imshow('Adaptive Threshold', adaptive_thresh)
    # cv2.imshow('adedge',edgead)
    # cv2.imshow('edges',edges)
    cv2.imshow('edges1',edges1)
    # cv2.imshow('gray',gray)

    

    circles = cv2.HoughCircles(edges1, cv2.HOUGH_GRADIENT, 0.7,70,
                            param1=100, param2=70, minRadius=50, maxRadius=0)    #ʶ��Բ��
    flag = 0
    detx = 0 #�����Ĳ��
    dety = 0
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
            detx = largest_circle[0] - w/2 -correct_x
            dety = h/2 - largest_circle[1] -correct_y
            pi=math.pi
            area=largest_circle[2]*largest_circle[2]*pi
            area_text=f"{area}"
            cv2.putText(res1, area_text, (largest_circle[0], largest_circle[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        cv2.putText(res1, 'no', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    # print(detx,dety)
    cv2.imshow("2",res1)
    if abs(detx)<4 and abs(dety)<4:
        if abs(detx)!= 0 or abs(detx)!= 0:
            stop_flag = 1
    return detx,dety,stop_flag


def findBlockCenter(color_cap,color_number):#color_number Ϊ 1 �������ɫ��Ϊ 2 �������ɫ��Ϊ 3 �������ɫ
    flag_color_1 = 0
    red_min   =  np.array(dim_red_min)
    red_max   =  np.array(dim_red_max)
    green_min =  np.array(dim_green_min)
    green_max =  np.array(dim_green_max)
    blue_min  =  np.array(dim_blue_min)   
    blue_max  =  np.array(dim_blue_max)  
    red_min1   = np.array(dim_red_min1)  
    red_max1   = np.array(dim_red_max1)#��������ɫ��ֵ����ɫ��hsvɫ������h��С�Ĳ��ֺ�h�ܴ����������
    ret,frame = color_cap.read()
    ret,frame = color_cap.read()
    ret,frame = color_cap.read()
    # print("ret:",ret)
    corrected_frame=undistortion(frame,mtx,dist)
    
    y0,x0 = corrected_frame.shape[:2]
    frame_change = cv2.resize(corrected_frame, (int(x0), int(y0)))

    src1 = frame_change.copy()
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
    for cnt343 in contours:
        (x1, y1, w1, h1) = cv2.boundingRect(cnt343)  # �ú������ؾ����ĸ���
        area = cv2.contourArea(cnt343)
        # if w1*h1 > 0.10*w*h:
        if area > 0.07*w*h:
            a = x1 + w1 / 2
            b = y1 + h1 / 2
            a_sum +=a
            b_sum +=b
            num += 1
            # print("color",num,":",a/w, b/h)
            # s=(x1+w1)*(y1+h1)
            
            cv2.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2)  # ����⵽����ɫ������
            cv2.putText(frame, 'color', (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            area_text=f"{area}"
            cv2.putText(frame, area_text, (x1+60, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            center_text = f"({a}, {b})"
            cv2.putText(res1, center_text, (x1, y1+h1+5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            color_text=f"{color_number}"
            cv2.putText(frame, color_text, (x1, y1+h1+10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            
            if num == 1 or c < y1:
                x_center = a
                y_center = b
                c = y1
            flag_color_1 = 1
            detx_p = a - w/2 - correct_x
            dety_p = h/2 - correct_y - b
            detx_p = int(detx_p)
            dety_p = int(dety_p)
    cv2.waitKey(1)
    return x_center/ w,y_center/h,frame,flag_color_1

def detectPlate(camera_cap,color_number):  #���Բ���˶�
    success, frame = camera_cap.read()  #ѡ��Ҫʶ�����ɫ  1��2��3��
    # print("success:",success)
    # cv2.imshow("origin",frame)

    global turn_direction
    cnt2 = 0
    x_add = 0
    y_add = 0
    get_blog = 0
    flag_stop = 0
    while(cnt2 < 5.5): #��������Ƭ������ɫ�����ĵ��ƶ��ȶ�
        
        global x_,y_
        x_,y_,img_,flag_= findBlockCenter(camera_cap,color_number)
        x_add = x_add + x_
        y_add = y_add + y_
        cv2.imshow("img",img_)
        cv2.waitKey(2)
        time.sleep(8e-2)
        cnt2 = cnt2 + 1
        get_blog = get_blog +flag_
    x_add = x_add /6
    y_add = y_add /6
    # print("get_blog",get_blog)
    if (abs(x_ - x_add) <0.01 and abs(y_ - y_add) < 0.01 and get_blog == 6): 
        #��6��ͼƬ���������ͼƬ��ɫ�����ĵ�ƽ���������һ�ε�ɫ������ ����ƫ��һ������ 
        #���жϸ���ɫɫ��û��ֹͣ������ֹͣ��
        flag_stop=1
    else:#��ɫ���ƶ���ʱ���ж�ɫ���������ƶ����������ƶ�
        if get_blog == 6:
            if((x_ - x_add)>0.02 ):
                turn_direction = True
            if((x_ - x_add)<-0.02 ):
                turn_direction = False
        flag_stop=0 
    print("flag:",flag_stop)
    cv2.waitKey(1)
    return flag_stop


def detectLine(cap):#��⳵���Ƿ���ֱ��ƽ��
    ret,frame = cap.read()
    ret,frame = cap.read()
    ret,frame = cap.read()
    cnt_line = 0
    # gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    # cv2.imshow("gray",gray)
    # edges = cv2.Canny(gray,50,150,apertureSize = 3)
    # cv2.imshow("1",frame)
    corrected_frame=undistortion(frame,mtx,dist)
    # cv2.imshow("correct",corrected_frame)
    
    gray = cv2.cvtColor(corrected_frame, cv2.COLOR_BGR2GRAY)   #ת�Ҷ�ͼ
    equalized = cv2.equalizeHist(gray)
    cv2.imshow("junheng",equalized)
    ret, thresh = cv2.threshold(equalized, 120, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(equalized, cv2.MORPH_CLOSE, kernel)#������
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)
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
                cv2.line(corrected_frame,(x1,y1),(x2,y2),(0,0,255),2)
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
    cv2.imshow("line",corrected_frame)
    line_flag=0
    # if(abs(finaltheta)<0.8  and abs(finaltheta)>0.1):
    if abs(finaltheta)<0.5:
        line_flag=1
    # if finaltheta<-0.5 and finaltheta>-1.5:
    #     line_flag=1
    finaltheta=int(round(finaltheta))
    if (finaltheta==90 ):
        finaltheta=0
    cv2.waitKey(1)
    return finaltheta,line_flag

def code(code_cap):  #ʶ���ά��
    ret,frame = code_cap.read()
    ret,frame = code_cap.read()
    ret,frame = code_cap.read()
    cv2.imshow("frame",frame)
    barcodes = decode(frame)  
    flag = 0
    data = []
    cv2.waitKey(10)

    
    for barcode in barcodes:
        #rect = barcode.rect
        #x, y, w, h = rect
        #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        data = barcode.data.decode("utf8")
        print(data)
        #cv2.putText(frame, data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        #print("Result:" + data)#����ע�������Ľ�ע�Ϳ�����ʾ��ά��Ŀ��Լ���ά������
    if len(barcodes)>0:
        flag = 1
    return data,flag

def sort(data):  #��ȡ�Ķ�ά����Ϣת��Ϊ����
    color_order = []
    print(data,type(data))
    for i in data:
        if ( i == '1'):
            color_order.append(1)#��
        elif ( i == '2'):
            color_order.append(2)#��
        elif ( i == '3'):
            color_order.append(3)#��
    return color_order



def undistortion(img, mtx, dist):   #jibian 
    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # print('roi ', roi)

    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

    # crop the image
    x, y, w, h = roi
    if roi != (0, 0, 0, 0):
        dst = dst[y:y + h, x:x + w]

    return dst
