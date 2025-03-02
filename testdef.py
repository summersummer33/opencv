import cv2
import numpy as np
import math
import time
import serial 
from pyzbar.pyzbar import decode  #ɨ��ά��Ŀ�


#��ɫ��ֵ
dim_red_min =   [  0, 60 ,60]
dim_red_max =   [ 12,203, 255]
dim_green_min = [32,48,54]# 30 48 54   61/48/54 61 taida    #yuanhuan   nengkanqianlv
dim_green_max = [78,234,255]#78,234,255
dim_green_min1 = [40,48,54]# 30 48 54   61/48/54 61 taida    #zhuanpan   fanghuangse
dim_green_max1 = [78,234,255]#78,234,255
dim_blue_min =  [82,105,0]#100 60 80
dim_blue_max =  [120,255,255]#124 230 255
dim_red_min1 =   [  160, 50 ,50]
dim_red_max1 =   [ 180,255, 255]


dim_gray_min=[95,0,0]     #jiaozhengzhixian
dim_gray_max=[180,255,255]


# x=40 y=34  zai gao de shi hou wangyoul x+,wangxial y-
# 41 -20
#42 16
#67 -9

#cutiao
#new 35 11
#32 8


#new paw
#cedingzhi 30 13
correct_x=30
correct_y=13

#45 24

#xitiao
#new 42 4
#42 10
#celiangzhi 38 5
#yixiashi luangaizhi
#36 14

#new paw
#cedingzhi 33 9
correct_x_hough=42
correct_y_hough=13

# npzfile = np.load('calibrate.npz')
# mtx = npzfile['mtx']
# dist = npzfile['dist']


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
    time.sleep(0.1)

    # data_array = [0xAA,0xBB,data_hex,0xCC]
    # byte_array = bytearray(data_array)   
    # ser.write(byte_array) 

    return 0

def sendMessage2(ser,data1,data2):   #yuanhuan center
    if data1>=0:
        signal1=1
    else :
        signal1=2
        data1=abs(data1)
    if data1>254:
        data1=254
    if data2>=0:
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

# def sendmessage2(ser,data1,data2):
#     signal1=1 if data1>=0 else 2
#     data1=min(abs(data1),254)
#     signal2=1 if data2>=0 else 2
#     data2=min(abs(data2),254)

#     data_hex1=f"{data1:02X}"
#     data_hex2=f"{data2:02X}"
#     signal_hex1=f"{signal1:02X}"
#     signal_hex2=f"{signal2:02X}"

#     data_pack = signal_hex1+data_hex1+signal_hex2+data_hex2
#     ser.write(bytes.fromhex(data_pack))
#     print(data_pack)
#     time.sleep(0.1)
#     return 0


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
    if data1>=0:
        signal1=1
    else :
        signal1=2
        data1=abs(data1)
    data_hex1=hex(data1)[2:]
    data_hex1 = data_hex1.zfill(2)
    signal_hex1=hex(signal1)[2:]
    signal_hex1 = signal_hex1.zfill(2)
    data_pack = signal_hex1+data_hex1
    ser.write(bytes.fromhex(data_pack))
    print("angle direction:",data_pack)
    time.sleep(0.1)

    return 0

def sendMessage5(ser,data_l,data_x,data_y):   #line detect
    if data_l>=0:
        signal_l=1
    else :
        signal_l=2
        data_l=abs(data_l)
    if data_x>=0:
        signal_x=1
    else:
        signal_x=2
        data_x=abs(data_x)
    if data_x>254:
        data_x=254
    if data_y>=0:
        signal_y=1
    else:
        signal_y=2
        data_y=abs(data_y)
    if data_y>254:
        data_y=254
    data_l=hex(data_l)[2:]
    data_l = data_l.zfill(2)
    signal_l=hex(signal_l)[2:]
    signal_l = signal_l.zfill(2)
    data_x=hex(data_x)[2:]
    data_x= data_x.zfill(2)
    signal_x=hex(signal_x)[2:]
    signal_x = signal_x.zfill(2)
    data_y=hex(data_y)[2:]
    data_y = data_y.zfill(2)
    signal_y=hex(signal_y)[2:]
    signal_y = signal_y.zfill(2)
    data_pack = signal_l+data_l+signal_x+data_x+signal_y+data_y
    print("together:",data_pack)
    ser.write(bytes.fromhex(data_pack))
    print("together:",data_pack)
    time.sleep(0.1)

    return 0

# def sendMessage5(ser, data_l, data_x, data_y):
#     signal_l = 1 if data_l >= 0 else 2
#     signal_x = 1 if data_x >= 0 else 2
#     data_x = min(abs(data_x), 254)
#     signal_y = 1 if data_y >= 0 else 2
#     data_y = min(abs(data_y), 254)
#     data_pack = (
#         f"{signal_l:02X}{data_l:02X}"  # data_l
#         f"{signal_x:02X}{data_x:02X}"  # data_x
#         f"{signal_y:02X}{data_y:02X}"  # data_y
#     )
#     ser.write(bytes.fromhex(data_pack))
#     print("together:", data_pack)
#     time.sleep(0.1)
    
#     return 0



def together_line_circle(cap):
    ret=cap.grab()
    ret=cap.grab()
    ret=cap.grab()
    ret,frame = cap.read()


    cnt_line = 0
    src1 = frame.copy()
    res1 = src1.copy()
    h, w = res1.shape[:2]


    #####################line#################################
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   #ת�Ҷ�ͼ
    equalized = cv2.equalizeHist(gray)
    # cv2.imshow("junheng",equalized)
    # ret, thresh = cv2.threshold(equalized, 120, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(equalized, cv2.MORPH_CLOSE, kernel)#������
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
            
            if ((np.abs(theta)>=1.1) & (np.abs(theta)<=2.2)):
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
                cv2.line(res1,(x1,y1),(x2,y2),(0,0,255),2)
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
    # cv2.imshow("line",frame)
    line_flag=0
    if abs(finaltheta)<0.5:
        line_flag=1
    finaltheta=int(round(finaltheta))
    if (finaltheta==90 ):
        finaltheta=0

    #####################circle#################################
    blurred = cv2.GaussianBlur(equalized, (9, 9), 2)
    # edges = cv2.Canny(blurred, 50, 150)
    edges1 = cv2.Canny(blurred, 50, 150)
    cv2.imshow("edges1",edges1)

    contours, _ = cv2.findContours(edges1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    flag = 0
    detx = 0 
    dety = 0
    detx1=0
    dety1=0
    largest_circle = None
    largest_area = 0
    move_flag = 0
    stop_flag = 0
    for contour in contours:
    # �������������?    # ���������С����?        
        area = cv2.contourArea(contour)
        # print("area:",area)
        if area > largest_area:
            largest_area = area
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            if len(approx) > 7:  # Բ�εĽ��ƶ���α���Ӧ�ô���?
                largest_circle = approx
                # print("largest area:",largest_area)
                if largest_area > 10000 :
                    # cv2.drawContours(res1, [largest_circle], 0, (0, 0, 255), 3)
                    (x, y), radius = cv2.minEnclosingCircle(largest_circle)
                    center = (int(x), int(y))
                    radius = int(radius)
                    detx = x - w/2 - correct_x
                    dety = h/2 - correct_y - y
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
                    # print("x=",x,"y=",y)
                    # print("detx=",detx,"dety=",dety)
                    print('  detx1:',detx1,'  dety1:',dety1)
                else:
                    cv2.putText(res1, 'no', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    if abs(detx)<15 and abs(dety)<15:
        if detx1==0 and dety1 ==0:
            stop_flag=0
        else:
        # if abs(detx)!= 0 or abs(dety)!= 0:
            stop_flag = 1

    # green_min =  np.array(dim_green_min)
    # green_max =  np.array(dim_green_max)
    # hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV)
    # mask2 = cv2.inRange(hsv, green_min, green_max)
    # cv2.imshow("green",mask2)
    # x_g=0
    # y_g=0
    # w_g=0
    # h_g=0
    # contours_green, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # large_contours_green = []
    # for contour in contours_green:
    #     area = cv2.contourArea(contour)
    #     if area > 100 :
    #         large_contours_green.append(contour)
    # if large_contours_green:
    #     merged_contour_g = np.vstack(large_contours_green)
    #     x_g, y_g, w_g, h_g = cv2.boundingRect(merged_contour_g)
    #     cv2.rectangle(res1, (x_g, y_g), (x_g + w_g, y_g + h_g), (0, 255, 0), 2)


 
    # x_g_new = max(0, x_g - 50)
    # y_g_new = max(0, y_g - 50) 
    # w_g_new = min(640, x_g + w_g + 50) - x_g_new 
    # h_g_new = min(480, y_g + h_g + 50) - y_g_new  
    # cv2.rectangle(res1, (x_g_new, y_g_new), (x_g_new + w_g_new, y_g_new + h_g_new), (255, 255, 0), 2)

    # # ��ȡͼ��
    # img_green = edges1[y_g_new:(y_g_new + h_g_new), x_g_new:(x_g_new + w_g_new)]

    # # img_green=edges1[y_g:(y_g+h_g),x_g:(x_g+w_g)]


    # contours_g, _ = cv2.findContours(img_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # largest_circle_g = None
    # largest_area_g = 0

    # detx1=0
    # dety1=0
    # stop_flag = 0
    # x_incolor=0
    # y_incolor=0
    # for contour in contours_g:
    #     area = cv2.contourArea(contour)
    #     if area > largest_area_g:
    #         largest_area_g = area
    #         peri = cv2.arcLength(contour, True)
    #         approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    #         if len(approx) > 7:  
    #             largest_circle_g = approx
    # # ѭ�������󣬸��� largest_circle ��ֵ���������߼�
    # if largest_circle_g is not None and largest_area_g > 10000:
    #     (x, y), radius = cv2.minEnclosingCircle(largest_circle_g)
    #     x=x+x_g_new
    #     y=y+y_g_new
    #     center = (int(x), int(y))
    #     radius = int(radius)
    #     cv2.circle(res1, center, 2, (0, 0, 255), 3)  # ����Բ��
    #     cv2.circle(res1, center, radius, (0, 255, 0), 2)  # �������Բ
    #     center_text = f"({center[0]}, {center[1]}), radius: {radius}"
    #     text_position = (center[0] + 10, center[1] - 10)
    #     area_text = f"Area: {largest_area_g}"
    #     cv2.putText(res1, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    #     cv2.putText(res1, area_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    #     x_incolor=x-correct_x-w/2
    #     y_incolor=h/2-y-correct_y
    #     detx1=int(round(x_incolor))
    #     dety1=int(round(y_incolor))
    #     print("cccccccccccccccccccccccccccccccccccccc")
    # else:
    #     cv2.putText(res1, 'No circle found', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    #     detx1=int(round(x_g_new + w_g_new/2 -w/2 -correct_x))
    #     dety1=int(round(h/2 - y_g_new - h_g_new/2 -correct_y))
    #     print("nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")

    # print("detx1:",detx1,"dety1:",dety1)


    # if abs(x_incolor)<15 and abs(y_incolor)<15:
    #     if abs(x_incolor)!= 0 or abs(y_incolor)!= 0:
    #         stop_flag = 1
    #         print("11111111111111111")
    cv2.imshow("res1",res1)
    frame=None
    cv2.waitKey(1)
    return finaltheta,line_flag,detx1,dety1,stop_flag

flag_in=0
cutiaocishu=0
def together_line_circle1(cap):  #in green
    ret=cap.grab()
    ret=cap.grab()
    ret=cap.grab()
    ret,frame = cap.read()


    cnt_line = 0
    src1 = frame.copy()
    res1 = src1.copy()
    h, w = res1.shape[:2]


    #####################line#################################
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   #ת�Ҷ�ͼ
    equalized = cv2.equalizeHist(gray)
    # cv2.imshow("junheng",equalized)
    # ret, thresh = cv2.threshold(equalized, 120, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(equalized, cv2.MORPH_CLOSE, kernel)#������
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
            
            if ((np.abs(theta)>=1.1) & (np.abs(theta)<=2.2)):
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
                cv2.line(res1,(x1,y1),(x2,y2),(0,0,255),2)
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
    # cv2.imshow("line",frame)
    line_flag=0
    if abs(finaltheta)<0.5:
        line_flag=1
    finaltheta=int(round(finaltheta))
    if (finaltheta==90 ):
        finaltheta=0

    #####################circle#################################
    blurred = cv2.GaussianBlur(equalized, (9, 9), 2)
    # edges = cv2.Canny(blurred, 50, 150)
    edges1 = cv2.Canny(blurred, 50, 150)
    cv2.imshow("edges1",edges1)


    green_min =  np.array(dim_green_min)
    green_max =  np.array(dim_green_max)
    hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV)
    mask2 = cv2.inRange(hsv, green_min, green_max)
    cv2.imshow("green",mask2)
    x_g=0
    y_g=0
    w_g=0
    h_g=0
    contours_green, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    large_contours_green = []
    for contour in contours_green:
        area = cv2.contourArea(contour)
        if area > 100 :
            large_contours_green.append(contour)
    if large_contours_green:
        merged_contour_g = np.vstack(large_contours_green)
        x_g, y_g, w_g, h_g = cv2.boundingRect(merged_contour_g)
        cv2.rectangle(res1, (x_g, y_g), (x_g + w_g, y_g + h_g), (0, 255, 0), 2)


 
    x_g_new = max(0, x_g - 50)
    y_g_new = max(0, y_g - 50) 
    w_g_new = min(1280, x_g + w_g + 50) - x_g_new 
    h_g_new = min(720, y_g + h_g + 50) - y_g_new  
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
    cv2.rectangle(res1, (x_g_new, y_g_new), (x_g_new + w_g_new, y_g_new + h_g_new), (255, 255, 0), 2)

    # ��ȡͼ��
    img_green = edges1[y_g_new:(y_g_new + h_g_new), x_g_new:(x_g_new + w_g_new)]

    # img_green=edges1[y_g:(y_g+h_g),x_g:(x_g+w_g)]


    contours_g, _ = cv2.findContours(img_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_circle_g = None
    largest_area_g = 0

    detx1=0
    dety1=0
    stop_flag = 0
    x_incolor=0
    y_incolor=0
    for contour in contours_g:
        area = cv2.contourArea(contour)
        if area > largest_area_g:
            largest_area_g = area
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            if len(approx) > 7:  
                largest_circle_g = approx
    # ѭ�������󣬸��� largest_circle ��ֵ���������߼�
    if largest_circle_g is not None and largest_area_g > 15000:
        #! !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        (x, y), radius = cv2.minEnclosingCircle(largest_circle_g)
        x=x+x_g_new
        y=y+y_g_new
        center = (int(x), int(y))
        radius = int(radius)
        cv2.circle(res1, center, 2, (0, 0, 255), 3)  # ����Բ��
        cv2.circle(res1, center, radius, (0, 255, 0), 2)  # �������Բ
        center_text = f"({center[0]}, {center[1]}), radius: {radius}"
        text_position = (center[0] + 10, center[1] - 10)
        area_text = f"Area: {largest_area_g}"
        cv2.putText(res1, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.putText(res1, area_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        x_incolor=x-correct_x-w/2
        y_incolor=h/2-y-correct_y
        detx1=int(round(x_incolor))
        dety1=int(round(y_incolor))
        print("cccccccccccccccccccccccccccccccccccccc")
        global flag_in
        flag_in=1
    else:
        cv2.putText(res1, 'No circle found', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        detx1=int(round(x_g_new + w_g_new/2 -w/2 -correct_x))
        dety1=int(round(h/2 - y_g_new - h_g_new/2 -correct_y))
        print("nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")



    # if flag_in ==0:
    #     detx1=int(round(x_g_new + w_g_new/2 -w/2 -correct_x))
    #     dety1=int(round(h/2 - y_g_new - h_g_new/2 -correct_y))
    #     print("nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn",flag_in)
    # else:
    #     detx1=int(round(x_incolor))
    #     dety1=int(round(y_incolor))
    #     print("cccccccccccccccccccccccccccccccccccccc",flag_in)
    left=-6
    right=0    #6
    print("detx1:",detx1,"dety1:",dety1)
    # if cutiaocishu % 2 ==0:
    #     left=-6
    #     right=6
    # else:
    #     left=-2
    #     right=6

    if (x_incolor<right and x_incolor>left) and abs(y_incolor)<6:
        if x_incolor == 0 and y_incolor==0:
            stop_flag=0
        else:
        # if abs(x_incolor)!= 0 or abs(y_incolor)!= 0:
            stop_flag = 1
            print("11111111111111111")
    cv2.imshow("res1",res1)
    frame=None
    cv2.waitKey(1)
    global cutiaocishu
    cutiaocishu += 1
    return finaltheta,line_flag,detx1,dety1,stop_flag


def findCountours(camera_cap): #ʶ��Բ��  ���ζ�λ
    success, frame = camera_cap.read()
    # frame = None
    success, frame = camera_cap.read()
    success, frame = camera_cap.read()
    success, frame = camera_cap.read()
    # success, frame = camera_cap.read()
    # cv2.imshow("origin",frame)

    # corrected_frame=undistortion(frame,mtx,dist)
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
    ################cv2.imshow("edges1",edges1)
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


def findContours_ifgreen(camera_cap):
    success = camera_cap.grab()
    success = camera_cap.grab()
    success = camera_cap.grab()
    success, frame = camera_cap.read()
    # cv2.imshow("origin",frame)

    # corrected_frame=undistortion(frame,mtx,dist)
    src1 = frame.copy()
    res1 = src1.copy()
    h, w = res1.shape[:2]

    ################
    ##Բ���ж�
    gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)   
    equalized = cv2.equalizeHist(gray)
    # cv2.imshow("junheng",equalized)
    blurred = cv2.GaussianBlur(equalized, (9, 9), 2)
    edges = cv2.Canny(blurred, 50, 150)
    cv2.imshow("edges",edges)
    # contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # largest_circle = None
    # largest_area = 0
    # radius = 0
    # x=0
    # y=0

    # for contour in contours:
    #     area = cv2.contourArea(contour)
    #     if area > largest_area:
    #         largest_area = area
    #         peri = cv2.arcLength(contour, True)
    #         approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    #         if len(approx) > 7:  
    #             largest_circle = approx

    # # ѭ�������󣬸��� largest_circle ��ֵ���������߼�
    # if largest_circle is not None and largest_area > 10000:
    #     (x, y), radius = cv2.minEnclosingCircle(largest_circle)
    #     center = (int(x), int(y))
    #     radius = int(radius)
    #     cv2.circle(res1, center, 2, (0, 0, 255), 3)  # ����Բ��
    #     cv2.circle(res1, center, radius, (0, 255, 0), 2)  # �������Բ
    #     center_text = f"({center[0]}, {center[1]}), radius: {radius}"
    #     text_position = (center[0] + 10, center[1] - 10)
    #     area_text = f"Area: {largest_area}"
    #     cv2.putText(res1, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    #     cv2.putText(res1, area_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    # else:
    #     cv2.putText(res1, 'No circle found', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
    ################
    ##��ɫ�ж�
    red_min   = np.array([  0, 60,  60])
    red_max   = np.array([ 12, 203, 255])
    blue_min  = np.array([94,  50, 80])
    blue_max  = np.array([133, 230, 255])
    red_min1   = np.array([  155, 43,  46])
    red_max1   = np.array([ 180, 255, 255])

    hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV)
    mask12 = cv2.inRange(hsv,   red_min,   red_max)
    mask11 = cv2.inRange(hsv,   red_min1,   red_max1)
    mask1 = cv2.add(mask12,mask11)  #��ɫ����
    mask3 = cv2.inRange(hsv,  blue_min,  blue_max)   #��ɫ����
    # mask_not_red_blue = cv2.bitwise_not(src1,src1,mask_notgreen)
    # cv2.imshow("not green",mask_not_red_blue)
    # ���������еķ�����������
    red_pixels = cv2.countNonZero(mask1)
    blue_pixels = cv2.countNonZero(mask3)
    print("red_pixels:",red_pixels,"blue_pixels:",blue_pixels)
    #��Ҫ���ݾ�����뿴���Ĵ�С�ټ�һ��ʶ�����ظ�����Χ�ж�
    color = None
    if red_pixels > blue_pixels:
        color = "Red"
    elif blue_pixels > red_pixels:
        color = "Blue"
    else:
        color = "Unknown"
    #������ɫ
    x_r=640
    y_r=0
    w_r=0
    h_r=0
    contours_red, _ = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    large_contours_red = []
    for contour in contours_red:
        area = cv2.contourArea(contour)
        if area > 100 :
            large_contours_red.append(contour)
    if large_contours_red:
        merged_contour_r = np.vstack(large_contours_red)
        x_r, y_r, w_r, h_r = cv2.boundingRect(merged_contour_r)
        cv2.rectangle(res1, (x_r, y_r), (x_r + w_r, y_r + h_r), (0, 0, 255), 2)
    x_b=0
    y_b=0
    w_b=0
    h_b=0
    contours_blue, _ = cv2.findContours(mask3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    large_contours_blue = []
    for contour in contours_blue:
        area = cv2.contourArea(contour)
        if area > 100 :
            large_contours_blue.append(contour)
    if contours_blue:
        merged_contour_b = np.vstack(contours_blue)
        x_b, y_b, w_b, h_b = cv2.boundingRect(merged_contour_b)
        cv2.rectangle(res1, (x_b, y_b), (x_b + w_b, y_b + h_b), (255, 0, 0), 2)

    img_portion=[None]*2
    img_portion[0]=edges[y_r:(y_r+h_r),x_r:(x_r+w_r)]   #red
    img_portion[1]=edges[y_b:(y_b+h_b),x_b:(x_b+w_b)]   #blue
    # circle_incolor = np.zeros(2).tolist()
    x_incolor=0
    y_incolor=0
    flag_incolor=5
    # cv2.imshow("1",img_portion[0])

    for i in range(2):
        contours, _ = cv2.findContours(img_portion[i], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        largest_circle = None
        largest_area = 0
        radius = 0
        x=0
        y=0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > largest_area:
                largest_area = area
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                if len(approx) > 7:  
                    largest_circle = approx

        # ѭ�������󣬸��� largest_circle ��ֵ���������߼�
        if largest_circle is not None and largest_area > 10000:
            (x, y), radius = cv2.minEnclosingCircle(largest_circle)
            flag_incolor=i
            if i==0:
                x=x+x_r
                y=y+y_r
            else:
                x=x+x_b
                y=y+y_b
            center = (int(x), int(y))
            radius = int(radius)
            cv2.circle(res1, center, 2, (0, 0, 255), 3)  # ����Բ��
            cv2.circle(res1, center, radius, (0, 255, 0), 2)  # �������Բ
            center_text = f"({center[0]}, {center[1]}), radius: {radius}"
            text_position = (center[0] + 10, center[1] - 10)
            area_text = f"Area: {largest_area}"
            cv2.putText(res1, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(res1, area_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            x_incolor=x-correct_x-w/2
            y_incolor=y-correct_y
            # flag_incolor=i

        else:
            cv2.putText(res1, 'No circle found', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    move_direction = 0
    move_distance = 0   
    print("x_incolor:",x_incolor)

    if flag_incolor != 5:
        if flag_incolor==0:   #red

            move_direction=1  #left
        elif flag_incolor==1:  #blue
            move_direction=2  #right
        # if x_incolor
        #     move_distance=

    # if radius:
    #     # if x<(x_b+w_b) or x>x_r:   
    #     if x>x_r:
    #         move_direction=1   #����
    #         move_distance = 11111
    #     elif x<(x_b+w_b):
    #         move_direction=2   #����
    #         move_distance = 11111
    else:
        if color == 'Red':
            move_direction=1   #����
            move_distance = 22222
        elif color == 'Blue':
            move_direction=2   #����
            move_distance = 22222
    # green_min =  np.array(dim_green_min)
    # green_max =  np.array(dim_green_max)
    # mask2 = cv2.inRange(hsv, green_min, green_max)
    # cv2.imshow("green",mask2)
    cv2.imshow("res1",res1)
    cv2.imshow("maskred",mask1)
    cv2.imshow("maskblue",mask3)
    # print("x:",x,"x_b+w_b:",x_b+w_b,"x_r:",x_r)
    # print("radius:",radius)
    print("direction:",move_direction,"distance:",move_distance)
    return move_direction,move_distance
    



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
    # success, frame = cap.read()
    # success, frame = cap.read()
    success=cap.grab()
    success=cap.grab()
    success=cap.grab()
    success, frame = cap.read()
    # corrected_frame=undistortion(frame,mtx,dist)
    # cv2.imshow("corrected",frame)
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
#     # cv2.imshow('adedge',edgead)
#     # cv2.imshow('edges',edges)
#     cv2.imshow('edges1',edges1)
    # cv2.imshow('gray',gray)

    gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)   #ת�Ҷ�ͼ
    equalized = cv2.equalizeHist(gray)
    # cv2.imshow("junheng",equalized)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(equalized, cv2.MORPH_CLOSE, kernel)#������
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)

    blurred = cv2.GaussianBlur(closed1, (9, 9), 2)
    blurred1 = cv2.GaussianBlur(equalized, (9, 9), 2)
    # cv2.imshow("junheng",blurred)
    edges = cv2.Canny(blurred, 50, 150)
    # cv2.imshow("xitiaoedge:",edges)

    circles = cv2.HoughCircles(blurred1, cv2.HOUGH_GRADIENT, 0.7,70,
                            param1=100, param2=65, minRadius=218, maxRadius=233)    #5th circle
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #640/480------140/155
    #minradius 124  param2:65 param1:100  128
    # circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 0.7,70,
    #                         param1=100, param2=45, minRadius=165, maxRadius=185)    #6th circle
    flag = 0
    detx = 0 #�����Ĳ��
    dety = 0
    detx1 = 10000
    dety1 = 10000
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
            detx = largest_circle[0] - w/2 -correct_x_hough
            dety = h/2 - largest_circle[1] -correct_y_hough
            detx1 = int(round(detx))
            dety1 = int(round(dety))
            print("detx=",detx,"dety=",dety)
            # print("detx1=",detx1,"dety1=",dety1)
            # pi=math.pi
            # area=largest_circle[2]*largest_circle[2]*pi
            # area_text=f"{area}"
            # cv2.putText(res1, area_text, (largest_circle[0], largest_circle[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        cv2.putText(res1, 'no', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    # print(detx,dety)
    cv2.imshow("2",res1)
    if abs(detx)<4 and abs(dety)<4:
        stop_flag=1
    # if abs(detx)<3 and abs(dety)<3:
        # if (detx1 == 10000) and (dety1 == 10000):
        #     stop_flag = 0
        # elif (detx!=0) and (dety==0):
        #     stop_flag = 1
        # elif (detx==0) and (dety!=0):
        #     stop_flag=1
        # elif (detx!=0) and (dety!=0):
        #     stop_flag=1
    if (detx1 == 10000) and (dety1 == 10000):
        detx1=0
        dety1=0
    print("detx1=",detx1,"dety1=",dety1,"stop_flag:",stop_flag)
    cv2.waitKey(1)
    return detx1,dety1,stop_flag

def circlePut_color(color_cap,color_number):#color_number Ϊ 1 �������ɫ��Ϊ 2 �������ɫ��Ϊ 3 �������ɫ
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
    
    y0,x0 = frame.shape[:2]
    frame_change = cv2.resize(frame, (int(x0), int(y0)))

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
    detx_p=10000
    dety_p=10000
    largest = None
    largest_area=0
    flag_color_1 = 0


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
        detx_p = a - w/2 - correct_x_hough
        dety_p = h/2 - correct_y_hough - b
        detx_p = int(detx_p)
        dety_p = int(dety_p)
        # print("detx_p:",detx_p,"dety_p:",dety_p)
    if abs(detx_p)<12 and abs(dety_p)<12:
        flag_color_1 =1
    if (detx_p==10000) and (dety_p==10000):
        detx_p=0
        dety_p=0
    cv2.imshow("src1",src1)
    print("detx_p:",detx_p,"dety_p:",dety_p,"flag_color_1:",flag_color_1)
    cv2.waitKey(1)
    return x_center/ w,y_center/h,frame,flag_color_1,detx_p,dety_p

def findBlockCenter(color_cap,color_number):#color_number Ϊ 1 �������ɫ��Ϊ 2 �������ɫ��Ϊ 3 �������ɫ
    flag_color_1 = 0
    red_min   =  np.array(dim_red_min)
    red_max   =  np.array(dim_red_max)
    green_min =  np.array(dim_green_min1)
    green_max =  np.array(dim_green_max1)
    blue_min  =  np.array(dim_blue_min)   
    blue_max  =  np.array(dim_blue_max)  
    red_min1   = np.array(dim_red_min1)  
    red_max1   = np.array(dim_red_max1)
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret,frame = color_cap.read()
    # print("ret:",ret)
    # corrected_frame=undistortion(frame,mtx,dist)
    
    y0,x0 = frame.shape[:2]
    frame_change = cv2.resize(frame, (int(x0), int(y0)))

    src1 = frame_change.copy()
    res1 = src1.copy()
    hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV)   

    # # Define the coordinates for the masked regions
    # # Mask the bottom-left region (x1, y1, w1, h1)
    # x1, y1, w1, h1 = 0, int(y0 * 0.75), int(x0 * 0.25), int(y0 * 0.25)  # Bottom-left region

    # # Mask the bottom-right region (x2, y2, w2, h2)
    # x2, y2, w2, h2 = int(x0 * 0.75), int(y0 * 0.75), int(x0 * 0.25), int(y0 * 0.25)  # Bottom-right region

    # # Set the pixel values in the masked regions to invalid values
    # hsv[y1:y1+h1, x1:x1+w1] = 0  # Mask the bottom-left region
    # hsv[y2:y2+h2, x2:x2+w2] = 0  # Mask the bottom-right region




    mask12 = cv2.inRange(hsv,   red_min,   red_max)
    mask11 = cv2.inRange(hsv,   red_min1,   red_max1)
    mask2 = cv2.inRange(hsv, green_min, green_max)
    mask3 = cv2.inRange(hsv,  blue_min,  blue_max)
    mask1 = cv2.add(mask12,mask11)
    if color_number == 1:
        mask0 = mask1
    elif color_number == 2:
        mask0 = mask2
    elif color_number == 3:
        mask0 = mask3
    res1 = cv2.bitwise_and(src1, src1, mask=mask0)   
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
        if w1*h1 > 0.07*w*h:
        # if area > 0.07*w*h:
            a = x1 + w1 / 2
            b = y1 + h1 / 2
            a_sum +=a
            b_sum +=b
            num += 1
            # print("color",num,":",a/w, b/h)
            # s=(x1+w1)*(y1+h1)
            
            cv2.rectangle(src1, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2)  # ����⵽����ɫ������
            cv2.putText(src1, 'color', (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            # area_text=f"{area}"
            area_text=f"{w1*h1}"
            cv2.putText(src1, area_text, (x1+60, y1 +h1+ 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            center_text = f"({a}, {b})"
            cv2.putText(src1, center_text, (x1, y1+h1+5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            color_text=f"{color_number}"
            cv2.putText(src1, color_text, (x1, y1+h1+10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            
            if num == 1 or c < y1:
                x_center = a
                y_center = b
                c = y1
            flag_color_1 = 1
            detx_p = a - w/2 - correct_x_hough
            dety_p = h/2 - correct_y_hough - b
            detx_p = int(detx_p)
            dety_p = int(dety_p)
    cv2.imshow("src1",src1)
    cv2.waitKey(1)
    return x_center/ w,y_center/h,frame,flag_color_1,detx_p,dety_p

def findBlockCenter_gray(color_cap):#put on plate sekuai
    color_number=0
    flag_color_1 = 0
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret,frame = color_cap.read()
    # print("ret:",ret)
    # corrected_frame=undistortion(frame,mtx,dist)
    
    y0,x0 = frame.shape[:2]
    frame_change = cv2.resize(frame, (int(x0), int(y0)))

    src1 = frame_change.copy()
    res1 = src1.copy()
    h, w = res1.shape[:2]
    hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV)    # ��BGRͼ��ת��ΪHSVͼ��
    cv2.imshow("res1",res1)

    #red
    # x_r=0
    # y_r=0
    # w_r=0
    # h_r=0
    # contours_red, _ = cv2.findContours(mask1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # large_contours_red = []
    # for contour in contours_red:
    #     area = cv2.contourArea(contour)
    #     if area > 100 :
    #         large_contours_red.append(contour)
    # if large_contours_red:
    #     merged_contour_r = np.vstack(large_contours_red)
    #     x_r, y_r, w_r, h_r = cv2.boundingRect(merged_contour_r)
    #     cv2.rectangle(res1, (x_r, y_r), (x_r + w_r, y_r + h_r), (0, 0, 255), 2)
    #     color_number=1

    #green
    # x_g=0
    # y_g=0
    # w_g=0
    # h_g=0
    # contours_green, _ = cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # large_contours_green = []
    # for contour in contours_green:
    #     area = cv2.contourArea(contour)
    #     if area > 100 :
    #         large_contours_green.append(contour)
    # if large_contours_green:
    #     merged_contour_g = np.vstack(large_contours_green)
    #     x_g, y_g, w_g, h_g = cv2.boundingRect(merged_contour_g)
    #     cv2.rectangle(res1, (x_g, y_g), (x_g + w_g, y_g + h_g), (0, 255, 0), 2)
    #     color_number=2

    #blue
    # x_b=0
    # y_b=0
    # w_b=0
    # h_b=0
    # contours_blue, _ = cv2.findContours(mask3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # large_contours_blue = []
    # for contour in contours_blue:
    #     area = cv2.contourArea(contour)
    #     if area > 100 :
    #         large_contours_blue.append(contour)
    # if contours_blue:
    #     merged_contour_b = np.vstack(contours_blue)
    #     x_b, y_b, w_b, h_b = cv2.boundingRect(merged_contour_b)
    #     cv2.rectangle(res1, (x_b, y_b), (x_b + w_b, y_b + h_b), (255, 0, 0), 2)
    #     color_number=3


    # h, w = res1.shape[:2]
    # blured = cv2.blur(res1, (7, 7))#�˲�
    # blured = cv2.blur(res1, (5, 5))
    # ret, bright = cv2.threshold(blured, 10, 255, cv2.THRESH_BINARY)#��ֵ��
    
    # gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)
    # h_g, w_g = gray.shape[:2]
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    # opened = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)#������
    # closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    # closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)
    # cv2.imshow("closed",closed)

    # contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)#����������ڻ�ȡɫ�鷶Χ
    # num = 0
    # a_sum=0
    # b_sum=0
    # x_min = 4000
    # x_max = 0
    # y_min = 4000
    # y_max = 0
    # x_center = 0
    # y_center = 0
    # c = 0
    # detx_p=0
    # dety_p=0
    # for cnt343 in contours:
    #     (x1, y1, w1, h1) = cv2.boundingRect(cnt343)  # �ú������ؾ����ĸ���
    #     area = cv2.contourArea(cnt343)
    #     if w1*h1 > 0.07*w*h:
    #     # if area > 0.07*w*h:
    #         a = x1 + w1 / 2
    #         b = y1 + h1 / 2
    #         a_sum +=a
    #         b_sum +=b
    #         num += 1
    #         # print("color",num,":",a/w, b/h)
    #         # s=(x1+w1)*(y1+h1)
            
    #         cv2.rectangle(src1, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2)  # ����⵽����ɫ������
    #         cv2.putText(src1, 'color', (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    #         # area_text=f"{area}"
    #         area_text=f"{w1*h1}"
    #         cv2.putText(src1, area_text, (x1+60, y1 +h1+ 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    #         center_text = f"({a}, {b})"
    #         cv2.putText(src1, center_text, (x1, y1+h1+5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    #         color_text=f"{color_number}"
    #         cv2.putText(src1, color_text, (x1, y1+h1+10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            
    #         if num == 1 or c < y1:
    #             x_center = a
    #             y_center = b
    #             c = y1
    #         flag_color_1 = 1
    #         detx_p = a - w/2 - correct_x_hough
    #         dety_p = h/2 - correct_y_hough - b
    #         detx_p = int(detx_p)
    #         dety_p = int(dety_p)
    gray = cv2.cvtColor(src1, cv2.COLOR_BGR2GRAY)   #ת�Ҷ�ͼ
    equalized = cv2.equalizeHist(gray)
    # cv2.imshow("junheng",equalized)
    blurred = cv2.GaussianBlur(equalized, (9, 9), 2)
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
    edges1 = cv2.Canny(blurred, 50, 150)
    # cv2.imshow("blu",blurred)
    ################cv2.imshow("edges1",edges1)
    contours, _ = cv2.findContours(edges1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# ��ʼ������
    largest_circle = None
    largest_area = 0

    move_flag = 0
    stop_flag = 0
    x=0
    y=0

    # for contour in contours:
    # # �������������
    # # ���������С����
    #     area = cv2.contourArea(contour)
    #     # print("area:",area)
    #     if area > largest_area:
    #         largest_area = area
    #         peri = cv2.arcLength(contour, True)
    #         approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    #         if len(approx) > 5:  # Բ�εĽ��ƶ���α���Ӧ�ô���8
    #             largest_circle = approx
    #             # print("largest area:",largest_area)
    # if largest_area > 10000 and largest_circle is not None:
    #     cv2.drawContours(res1, [largest_circle], 0, (0, 0, 255), 3)
    #     # ����Բ�ĺͰ뾶
    #     (x, y), radius = cv2.minEnclosingCircle(largest_circle)
    #     # print("x=",x,"y=",y)
    #     center = (int(x), int(y))
    #     radius = int(radius)
    #     detx = x - w/2 - correct_x
    #     dety = h/2 - correct_y - y
    #     # print("detx=",detx,"dety=",dety)
    #     detx1 = int(round(detx))
    #     dety1 = int(round(dety))
    #     cv2.circle(res1, center, 2, (0, 0, 255), 3)
    #     # ����Բ
    #     cv2.circle(res1, center, radius, (0, 255, 0), 2)
    #     center_text = f"({center[0]}, {center[1]}), radius: {radius}"
    #     text_position = (center[0] + 10, center[1] - 10)
    #     area_text=f"({largest_area})"
    #     cv2.putText(res1, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    #     cv2.putText(res1, area_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    #     # print('  detx1:',detx1,'  dety1:',dety1)

    #     flag_color_1 = 1

    # if x<20 or x>620:

    blurred1 = cv2.GaussianBlur(equalized, (9, 9), 2)
    # cv2.imshow("junheng",blurred)
    edges = cv2.Canny(blurred, 50, 150)
    # cv2.imshow("xitiaoedge:",edges)

    circles = cv2.HoughCircles(blurred1, cv2.HOUGH_GRADIENT, 0.7,70,
                            param1=100, param2=65, minRadius=140, maxRadius=155)    #5th circle


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
            x=largest_circle[0]
            y=largest_circle[1]
            cv2.circle(res1, (largest_circle[0], largest_circle[1]), largest_circle[2], (0, 0, 255), 2)
        # �������ĵ�
            cv2.circle(res1, (largest_circle[0], largest_circle[1]), 2, (0, 0, 255), 3)
            center_text = f"({largest_circle[0]}, {largest_circle[1]})"
        # �����ı�λ�ã�ͨ����Բ���Ϸ�
            text_position = (largest_circle[0] + 10, largest_circle[1] - 10)
        # ��ͼ���ϻ���Բ������
            # cv2.putText(edges, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            radius = largest_circle[2]
            radius_text = f"Radius: {radius}"
            radius_position = (largest_circle[0] + 10, largest_circle[1] + 20)  # ѡ��һ�����ʵ�λ������ʾ�뾶��Ϣ
            cv2.putText(res1, radius_text, radius_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            detx = largest_circle[0] - w/2 -correct_x_hough
            dety = h/2 - largest_circle[1] -correct_y_hough
            detx1 = int(round(detx))
            dety1 = int(round(dety))
            flag_color_1 = 1
            # print("detx=",detx,"dety=",dety)
            print("detx1=",detx1,"dety1=",dety1)
    else:
        cv2.putText(res1, 'no', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.imshow("res1",res1)
    cv2.waitKey(1)
    return x/w,y/h,frame,flag_color_1,detx1,dety1,color_number

def findBlockCenter_circle(color_cap,color_number):#put on plate yuanhuan
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
    
    y0,x0 = frame.shape[:2]
    frame_change = cv2.resize(frame, (int(x0), int(y0)))

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
    equalized = cv2.equalizeHist(gray)
    h_g, w_g = gray.shape[:2]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)#������
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)
    blurred1 = cv2.GaussianBlur(equalized, (9, 9), 2)
    # cv2.imshow("junheng",blurred)
    # edges = cv2.Canny(blurred, 50, 150)
    # cv2.imshow("xitiaoedge:",edges)

    circles = cv2.HoughCircles(blurred1, cv2.HOUGH_GRADIENT, 0.7,70,
                            param1=100, param2=65, minRadius=140, maxRadius=155)    #5th circle
    # circles = cv2.HoughCircles(blurred1, cv2.HOUGH_GRADIENT, 0.7,70,
    #                         param1=100, param2=35, minRadius=160, maxRadius=185)    #6th circle
    flag = 0
    detx = 0 #�����Ĳ��
    dety = 0
    detx1 = 0
    dety1 = 0
    x_center=0
    y_center=0
    flag_color_1=0
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
            x_center=largest_circle[0]
            y_center=largest_circle[1]
            cv2.circle(src1, (largest_circle[0], largest_circle[1]), largest_circle[2], (0, 0, 255), 2)
        # �������ĵ�
            cv2.circle(src1, (largest_circle[0], largest_circle[1]), 2, (0, 0, 255), 3)
            center_text = f"({largest_circle[0]}, {largest_circle[1]})"
        # �����ı�λ�ã�ͨ����Բ���Ϸ�
            text_position = (largest_circle[0] + 10, largest_circle[1] - 10)
        # ��ͼ���ϻ���Բ������
            # cv2.putText(edges, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            radius = largest_circle[2]
            radius_text = f"Radius: {radius}"
            radius_position = (largest_circle[0] + 10, largest_circle[1] + 20)  # ѡ��һ�����ʵ�λ������ʾ�뾶��Ϣ
            cv2.putText(src1, radius_text, radius_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            detx = largest_circle[0] - w/2 -correct_x_hough
            dety = h/2 - largest_circle[1] -correct_y_hough
            detx1 = int(round(detx))
            dety1 = int(round(dety))
            flag_color_1 = 1
            # print("detx=",detx,"dety=",dety)
            print("detx1=",detx1,"dety1=",dety1)
    else:
        cv2.putText(res1, 'no', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    # x_g=0
    # y_g=0
    # w_g=0
    # h_g=0
    # x_center=0
    # y_center=0
    # flag_color_1 = 0
    # detx=0
    # dety=0
    # detx1=0
    # dety1=0
    # contours_green, _ = cv2.findContours(mask0, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # large_contours_green = []
    # # largest_area_green=0
    # for contour in contours_green:
    #     area = cv2.contourArea(contour)
    #     if area > 100 :
    #         large_contours_green.append(contour)
    # if large_contours_green:
    #     merged_contour_g = np.vstack(large_contours_green)
    #     x_g, y_g, w_g, h_g = cv2.boundingRect(merged_contour_g)
    #     cv2.rectangle(src1, (x_g, y_g), (x_g + w_g, y_g + h_g), (0, 255, 0), 2)
    #     print("area:",w_g*h_g)
    #     if w_g*h_g>80000:
    #         x_center = x_g + w_g / 2
    #         y_center = y_g + h_g / 2
    #         flag_color_1 =1
    #         # detx = x_center - w/2 -correct_x
    #         # dety = h/2 - y_center -correct_y
    #         # detx1 = int(round(detx))
    #         # dety1 = int(round(dety))



    # contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)#����������ڻ�ȡɫ�鷶Χ
    # num = 0
    # a_sum=0
    # b_sum=0
    # x_min = 4000
    # x_max = 0
    # y_min = 4000
    # y_max = 0
    # x_center = 0
    # y_center = 0
    # c = 0
    # detx_p=10000
    # dety_p=10000
    # largest = None
    # largest_area=0
    # flag_color_1 = 0


    # for contour in contours:
    # # �������������
    # # ���������С����
    #     area = cv2.contourArea(contour)
    #     # print("area:",area)
    #     if area > largest_area:
    #         largest_area = area
    #         largest=contour
    # if largest is not None and largest_area>70000: ##########################gaidong
    #     (x1, y1, w1, h1) = cv2.boundingRect(largest)
    #     x_center = x1 + w1 / 2
    #     y_center = y1 + h1 / 2
    #     print("area:",w1*h1)
    #     cv2.rectangle(src1, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2)  # ����⵽����ɫ������
    #     cv2.putText(src1, 'color', (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    #     area_text=f"{area}"
    #     cv2.putText(src1, area_text, (x1+60, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    #     center_text = f"({a}, {b})"
    #     cv2.putText(src1, center_text, (x1, y1+h1+5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    #     color_text=f"{color_number}"
    #     cv2.putText(src1, color_text, (x1, y1+h1+10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    #     detx_p = x_center - w/2 - correct_x_hough
    #     dety_p = h/2 - correct_y_hough - y_center
    #     detx_p = int(detx_p)
    #     dety_p = int(dety_p)
    #     flag_color_1 =1
        # print("detx_p:",detx_p,"dety_p:",dety_p)
    # if abs(detx_p)<12 and abs(dety_p)<12:
    #     flag_color_1 =1
    # if (detx_p==10000) and (dety_p==10000):
    #     detx_p=0
    #     dety_p=0
    cv2.imshow("src1",src1)
    # print("detx_p:",detx_p,"dety_p:",dety_p,"flag_color_1:",flag_color_1)
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
        x_,y_,img_,flag_,detx_,dety_= findBlockCenter(camera_cap,color_number)
        x_add = x_add + x_
        y_add = y_add + y_
        # cv2.imshow("img",img_)
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

def detectPlate_check(camera_cap,color_number):  #ת�̴�����Ƿ��Ѽ�ȡ���   
    success, frame = camera_cap.read()  #ѡ��Ҫʶ������? 1��2��3��
    # print("success:",success)
    # cv2.imshow("origin",frame)

    global turn_direction
    cnt2 = 0
    get_blog = 0
    flag_stop = 0
    x_add = 0
    y_add = 0
    times = 3
    while(cnt2 < times): #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!����δ��
        
        global x_,y_
        x_,y_,img_,flag_,detx,dety= findBlockCenter(camera_cap,color_number)
        print("x_:",x_,"y_:",y_,"flag_:",flag_)
        cv2.imshow("img",img_)
        cv2.waitKey(2)
        time.sleep(8e-2)
        cnt2 = cnt2 + 1
        x_add = x_add + x_
        y_add = y_add + y_
        get_blog = get_blog +flag_
    x_add = x_add /times
    y_add = y_add /times
    # if (abs(x_)<111) and (abs(y_)<111): #!!!!!!!!!!!!!!!!!!!!!!!!!��ֵδ��
    #     get_blog = get_blog +flag_
    if (abs(x_add-x_) <0.1 and abs(y_add-y_) < 0.1 and get_blog == times):  
        flag_stop=1
    # else:
    #     if get_blog == 6:
    #         if((x_ - x_add)>0.02 ):
    #             turn_direction = True
    #         if((x_ - x_add)<-0.02 ):
    #             turn_direction = False
    #     flag_stop=0 
    # if get_blog == times :
    #     flag_stop=1
    print("get_blog",get_blog,"flag:",flag_stop)
    cv2.waitKey(1)
    return flag_stop

def detectPlate_gray(camera_cap):  #put on the plate sekuai
    success, frame = camera_cap.read()  #ѡ��Ҫʶ�����ɫ  1��2��3��
    # print("success:",success)
    # cv2.imshow("origin",frame)

    global turn_direction
    cnt2 = 0
    x_add = 0
    y_add = 0
    get_blog = 0
    flag_stop = 0
    while(cnt2 < 4.5): #��������Ƭ������ɫ�����ĵ��ƶ��ȶ�
        
        global x_,y_
        x_,y_,img_,flag_,detx_,dety_,color_number= findBlockCenter_gray(camera_cap)
        x_add = x_add + x_
        y_add = y_add + y_
        # cv2.imshow("img",img_)
        cv2.waitKey(2)
        time.sleep(8e-2)
        cnt2 = cnt2 + 1
        get_blog = get_blog +flag_
    x_add = x_add /5
    y_add = y_add /5
    print("gray_getblog:",get_blog)
    # print("get_blog",get_blog)
    if (abs(x_ - x_add) <0.01 and abs(y_ - y_add) < 0.01 and get_blog == 5): 
        #��6��ͼƬ���������ͼƬ��ɫ�����ĵ�ƽ���������һ�ε�ɫ������ ����ƫ��һ������ 
        #���жϸ���ɫɫ��û��ֹͣ������ֹͣ��
        flag_stop=1
    else:#��ɫ���ƶ���ʱ���ж�ɫ���������ƶ����������ƶ�
        if get_blog == 5:
            if((x_ - x_add)>0.02 ):
                turn_direction = True
            if((x_ - x_add)<-0.02 ):
                turn_direction = False
        flag_stop=0 
    print("zhuanpantingzhi flag:",flag_stop)
    cv2.waitKey(1)
    return flag_stop

def detectPlate_circle(camera_cap,color_number):  #put on the plate yuanhuan
    success, frame = camera_cap.read()  #ѡ��Ҫʶ�����ɫ  1��2��3��
    # print("success:",success)
    # cv2.imshow("origin",frame)

    global turn_direction
    cnt2 = 0
    x_add = 0
    y_add = 0
    get_blog = 0
    flag_stop = 0
    times=3
    while(cnt2 < times): #��������Ƭ������ɫ�����ĵ��ƶ��ȶ�
        
        global x_,y_
        x_,y_,img_,flag_=findBlockCenter_circle(camera_cap,color_number)
        x_add = x_add + x_
        y_add = y_add + y_
        # cv2.imshow("img",img_)
        cv2.waitKey(2)
        time.sleep(8e-2)
        cnt2 = cnt2 + 1
        get_blog = get_blog +flag_
    x_add = x_add /times
    y_add = y_add /times
    print("gray_getblog:",get_blog)
    # print("get_blog",get_blog)
    if (abs(x_ - x_add) <0.01 and abs(y_ - y_add) < 0.01 and get_blog == times): 
        #��6��ͼƬ���������ͼƬ��ɫ�����ĵ�ƽ���������һ�ε�ɫ������ ����ƫ��һ������ 
        #���жϸ���ɫɫ��û��ֹͣ������ֹͣ��
        flag_stop=1
    else:#��ɫ���ƶ���ʱ���ж�ɫ���������ƶ����������ƶ�
        if get_blog == times:
            if((x_ - x_add)>0.02 ):
                turn_direction = True
            if((x_ - x_add)<-0.02 ):
                turn_direction = False
        flag_stop=0 
    print("zhuanpantingzhi flag:",flag_stop)
    cv2.waitKey(1)
    return flag_stop

def detectLine(cap):#��⳵���Ƿ���ֱ��ƽ��
    # if frame is not None:
    #     cv2.imshow('Frame', frame)
    # else:
    #     print("noooonononononon")
    # ret,frame = cap.read()
    # ret,frame = cap.read()
    # ret,frame = cap.read()
    # ret,frame = cap.read()
    # ret,frame = cap.read()
    ret=cap.grab()
    ret=cap.grab()
    ret=cap.grab()
    ret,frame = cap.read()
    # frame = cap.read()
    # frame = cap.read()
    # frame = cap.read()

    cnt_line = 0
    # gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    # cv2.imshow("gray",gray)
    # edges = cv2.Canny(gray,50,150,apertureSize = 3)
    # cv2.imshow("1",frame)
    # corrected_frame=undistortion(frame,mtx,dist)
    # cv2.imshow("correct",corrected_frame)
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   #ת�Ҷ�ͼ
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
    return finaltheta,line_flag



def detectLine_gray(color_cap):
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

    lines = cv2.HoughLines(edges,1,np.pi/180,threshold =120)#��ȡͼ�е���
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
