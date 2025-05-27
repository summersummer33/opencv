import cv2
import numpy as np
import math
import time
import serial 
from pyzbar.pyzbar import decode  


#颜色hsv
#绿色 hmin值太小会看见黄色 太大会看不见浅绿
dim_red_min =   [  0, 60 ,60]
dim_red_max =   [ 12,203, 255]
dim_green_min = [32,48,54]# 30 48 54   61/48/54 61 taida    #yuanhuan   nengkanqianlv
dim_green_max = [78,234,255]#78,234,255
dim_green_min1 = [40,48,54]# 30 48 54   61/48/54 61 taida    #zhuanpan   fanghuangse     40 48 54
dim_green_max1 = [78,234,255]#78,234,255
dim_blue_min =  [82,70,0]#100 60 80
dim_blue_max =  [120,255,255]#124 230 255
dim_red_min1 =   [  160, 50 ,50]
dim_red_max1 =   [ 180,255, 255]

#校正直线时分割黄、灰
dim_gray_min=[95,0,0] 
dim_gray_max=[180,255,255]

#转盘夹取物料 物料面积大小系数  0.039
block_area=0.039
#粗调时0.016
cutiao_center_circle=0.0097

#放的偏右了x值就+，偏下了y值就-

#new paw
#cedingzhi 30 13
#cedingzhi 39 -9
#42  -9
#粗调时高度偏差值(findcontours)
correct_x=42
correct_y=-9

#new paw
#cedingzhi 33 9
#celiangzhi 42 5
#houghcircles 43 7
#20thin---y=16
#用了很久  43  7 
#37  6
#细调时高度的偏差值(houghcircles)
correct_x_hough=37
correct_y_hough=6
#存储默认值
correct_x_hough_default=correct_x_hough
correct_y_hough_default=correct_y_hough

#摄像头分辨率
frameWidth = 1280
frameHeight = 720

#houghcircles半径限制值/第5环实线
# 640/480-----140/155
# 800/600-----186/197
# 1280/720----218/23
houghradius_min=187
houghradius_max=212

#houghcircles半径限制值/第6环虚线
# 640/480-----
# 800/600-----
# 1280/720----
houghradius_min_6th=209
houghradius_max_6th=233

###########################################################################################
###########################################################################################
###########################################################################################

def serialInit():  #初始化串口通信
    Pi_serial  =  serial.Serial( port="/dev/ttyAMA2",
                              baudrate=115200,
                              bytesize=serial.EIGHTBITS,
                              parity=serial.PARITY_NONE,
                              stopbits=serial.STOPBITS_ONE,
                              )
    return Pi_serial


def receiveMessage(ser):  #接收信息
    count = ser.inWaiting()
    if count != 0:
        recv = ser.read(count) 
        # recv_data=recv.hex()
        recv_data=recv
        # if recv[0] == 0xAA and recv[1] == 0xBB and recv[-1] == 0xCC:
        #     recv_useful = recv[2]  
        #     recv_data=recv_useful.hex()
        # else:
        #     recv_data = None  
    else:
        recv_data = None
    ser.flushInput()
    time.sleep(0.1)
    return recv_data


def sendMessage(ser,data):  #发送到位信息（单个正数
    data_hex=hex(data)[2:]
    data_hex = data_hex.zfill(2)
    # data_hex=data.to_bytes(1,'big')
    data_hex=bytes.fromhex(data_hex)
    pre='?'.encode()
    data_1=pre+data_hex
    # print(data_hex)
    # data_pack = 'AA'+'BB'+data_hex+'CC'
    # data_pack =data_hex
    # ser.write(bytes.fromhex(data))
    # ser.write(bytes.fromhex(data_hex))
    ser.write(data_1)
    print(data_1)
    time.sleep(0.01)
    # ser.write(data_1)

    return 0

# def sendMessage2(ser,data1,data2):   #发送圆环中心 分辨率为小数
#     if data1>=0:
#         signal1=1
#     else :
#         signal1=2
#         data1=abs(data1)
#     if data1>254:
#         data1=254
#     if data2>=0:
#         signal2=1
#     else:
#         signal2=2
#         data2=abs(data2)
#     if data2>254:
#         data2=254
#     data_hex1=hex(data1)[2:]
#     data_hex1 = data_hex1.zfill(2)
#     data_hex2=hex(data2)[2:]
#     data_hex2 = data_hex2.zfill(2)
#     signal_hex1=hex(signal1)[2:]
#     signal_hex1 = signal_hex1.zfill(2)
#     signal_hex2=hex(signal2)[2:]
#     signal_hex2 = signal_hex2.zfill(2)
#     # print(data_hex)
#     data_pack = signal_hex1+data_hex1+signal_hex2+data_hex2
#     # data_pack =data_hex
#     # ser.write(bytes.fromhex(data))
#     ser.write(bytes.fromhex(data_pack))
#     print(data_pack)
#     time.sleep(0.1)
#     return 0

def sendMessage2(ser, data1, data2):   #发送圆环中心 分辨率为大数 偏差值会大于一个16进制的最大数字255
    # 处理 data1
    if data1 >= 0:
        signal1 = 1
    else:
        signal1 = 2
        data1 = abs(data1)  # 取绝对值
    # 处理 data2
    if data2 >= 0:
        signal2 = 1
    else:
        signal2 = 2
        data2 = abs(data2)  # 取绝对值
    # 将数据和符号位转换为字节串（4字节，大端序）
    signal1_bytes = signal1.to_bytes(1, 'big')  # 符号位占1字节
    data1_bytes = data1.to_bytes(2, 'big')      # 数据占2字节
    signal2_bytes = signal2.to_bytes(1, 'big')  # 符号位占1字节
    data2_bytes = data2.to_bytes(2, 'big')      # 数据占2字节
    end='!'.encode()
    # 发送数据
    data_pack = signal1_bytes + data1_bytes + signal2_bytes + data2_bytes + end
    ser.write(data_pack)
    print(data_pack.hex().upper())  # 打印十六进制格式
    time.sleep(0.1)

    return 0


def sendMessage3(ser, data):    #发送二维码信息
    if isinstance(data, list):
        length = len(data)
        # processed_data = []
        combined_data_hex=''
        for item in data:
            data_hex = hex(item)[2:]
            data_hex = data_hex.zfill(2)
            # data_hex=item.to_bytes(1,'big')
            # processed_data.append(data_hex)
            combined_data_hex += data_hex
        pre='*'.encode()
        combined_data_hex=bytes.fromhex(combined_data_hex)
        combined_data_hex=pre+combined_data_hex
        print(f"Array length: {length}")
        # combined_data_hex = '+'.join(processed_data)
        # print(combined_data_hex)
        # ser.write(bytes.fromhex(combined_data_hex))
        ser.write(combined_data_hex)
        print(combined_data_hex)
        # print(combined_data_hex)
    else:
        data_hex = hex(data)[2:]
        data_hex = data_hex.zfill(2)
        ser.write(bytes.fromhex(data_hex))
        print(f"Single data: {data}")

def sendMessage4(ser,data1):   #/没在用/ 发送直线角度（单个数字带正负 角度
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

# def sendMessage5(ser,data_l,data_x,data_y):   #粗调 直线+圆心偏差 小分辨率
#     if data_l>=0:
#         signal_l=1
#     else :
#         signal_l=2
#         data_l=abs(data_l)
#     if data_x>=0:
#         signal_x=1
#     else:
#         signal_x=2
#         data_x=abs(data_x)
#     if data_x>254:
#         data_x=254
#     if data_y>=0:
#         signal_y=1
#     else:
#         signal_y=2
#         data_y=abs(data_y)
#     if data_y>254:
#         data_y=254
#     data_l=hex(data_l)[2:]
#     data_l = data_l.zfill(2)
#     signal_l=hex(signal_l)[2:]
#     signal_l = signal_l.zfill(2)
#     data_x=hex(data_x)[2:]
#     data_x= data_x.zfill(2)
#     signal_x=hex(signal_x)[2:]
#     signal_x = signal_x.zfill(2)
#     data_y=hex(data_y)[2:]
#     data_y = data_y.zfill(2)
#     signal_y=hex(signal_y)[2:]
#     signal_y = signal_y.zfill(2)
#     data_pack = signal_l+data_l+signal_x+data_x+signal_y+data_y
#     print("together:",data_pack)
#     ser.write(bytes.fromhex(data_pack))
#     print("together:",data_pack)
#     time.sleep(0.1)

#     return 0

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

def sendMessage5(ser, data_l, data_x, data_y):   #发送偏差值 粗调 直线+圆心偏差 大分辨率
    # 处理 data_l
    if data_l >= 0:
        signal_l = 1
    else:
        signal_l = 2
        data_l = abs(data_l)  # 取绝对值
    # 处理 data_x
    if data_x >= 0:
        signal_x = 1
    else:
        signal_x = 2
        data_x = abs(data_x)  # 取绝对值
    # 处理 data_y
    if data_y >= 0:
        signal_y = 1
    else:
        signal_y = 2
        data_y = abs(data_y)  # 取绝对值
    # 将数据和符号位转换为字节串（1字节，大端序）
    signal_l_bytes = signal_l.to_bytes(1, 'big')  # 符号位占1字节
    data_l_bytes = data_l.to_bytes(1, 'big')      # 数据占1字节
    signal_x_bytes = signal_x.to_bytes(1, 'big')  # 符号位占1字节
    data_x_bytes = data_x.to_bytes(2, 'big')      # 数据占2字节
    signal_y_bytes = signal_y.to_bytes(1, 'big')  # 符号位占1字节
    data_y_bytes = data_y.to_bytes(2, 'big')      # 数据占2字节
    end='!'.encode()
    # 发送数据
    data_pack = signal_l_bytes + data_l_bytes + signal_x_bytes + data_x_bytes + signal_y_bytes + data_y_bytes + end
    ser.write(data_pack)
    print("together:", data_pack.hex().upper())  # 打印十六进制格式
    time.sleep(0.1)
    return 0

def sendMessage6(ser, data):    #发送从右到左颜色（在一条直线三个圆环处夹取物料
    if isinstance(data, list):
        length = len(data)
        # processed_data = []
        combined_data_hex=''
        for item in data:
            data_hex = hex(item)[2:]
            data_hex = data_hex.zfill(2)
            # data_hex=item.to_bytes(1,'big')
            # processed_data.append(data_hex)
            combined_data_hex += data_hex
        pre='%'.encode()
        combined_data_hex=bytes.fromhex(combined_data_hex)
        combined_data_hex=pre+combined_data_hex
        print(f"Array length: {length}")
        # combined_data_hex = '+'.join(processed_data)
        # print(combined_data_hex)
        # ser.write(bytes.fromhex(combined_data_hex))
        ser.write(combined_data_hex)
        print(combined_data_hex)
        # print(combined_data_hex)
    else:
        data_hex = hex(data)[2:]
        data_hex = data_hex.zfill(2)
        ser.write(bytes.fromhex(data_hex))
        print(f"Single data: {data}")

#粗调 直线+圆（findContours 看中间圆环-绿色
flag_in=0
cutiaocishu=0
def together_line_circle1(cap):  #粗调 直线+圆（findContours 看中间圆环-绿色
    ret=cap.grab()
    ret=cap.grab()
    ret=cap.grab()
    ret,frame = cap.read()


    res1 = frame.copy()
    h, w = res1.shape[:2]

    #####################line图像处理#################################
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   #ת Ҷ ͼ
    equalized = cv2.equalizeHist(gray)
    # cv2.imshow("junheng",equalized)
    # ret, thresh = cv2.threshold(equalized, 120, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(equalized, cv2.MORPH_OPEN, kernel)#      
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    # closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)
    blurred = cv2.GaussianBlur(closed1, (9, 9), 2)
    edges = cv2.Canny(blurred, 50, 150)
    # cv2.imshow("edges",edges)

    #####################circle图像处理#################################
    blurred_c = cv2.GaussianBlur(equalized, (9, 9), 2)
    # edges = cv2.Canny(blurred, 50, 150)
    edges1 = cv2.Canny(blurred_c, 50, 150)
    cv2.imshow("edges1",edges1)

    red_min   =  np.array(dim_red_min)
    red_max   =  np.array(dim_red_max)
    green_min =  np.array(dim_green_min)
    green_max =  np.array(dim_green_max)
    blue_min  =  np.array(dim_blue_min)   
    blue_max  =  np.array(dim_blue_max)  
    red_min1   = np.array(dim_red_min1)  
    red_max1   = np.array(dim_red_max1)
    hsv = cv2.cvtColor(res1, cv2.COLOR_BGR2HSV)
    mask12 = cv2.inRange(hsv,   red_min,   red_max)
    mask11 = cv2.inRange(hsv,   red_min1,   red_max1)
    mask2 = cv2.inRange(hsv, green_min, green_max)
    mask3 = cv2.inRange(hsv,  blue_min,  blue_max)
    mask1 = cv2.add(mask12,mask11)
    cv2.imshow("green",mask2)

    ####不看颜色框里线，避免被物料直边干扰
    #red
    x_r=0
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
        edges[y_r:y_r + h_r, x_r:x_r + w_r] = 0
        cv2.rectangle(res1, (x_r, y_r), (x_r + w_r, y_r + h_r), (0, 0, 255), 2)

    #blue
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
    if large_contours_blue:
        merged_contour_b = np.vstack(large_contours_blue)
        x_b, y_b, w_b, h_b = cv2.boundingRect(merged_contour_b)
        edges[y_b:y_b + h_b, x_b:x_b + w_b] = 0
        cv2.rectangle(res1, (x_b, y_b), (x_b + w_b, y_b + h_b), (255, 0, 0), 2)


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
        edges[y_g:y_g + h_g, x_g:x_g + w_g] = 0
        cv2.rectangle(res1, (x_g, y_g), (x_g + w_g, y_g + h_g), (0, 255, 0), 2)
 
    x_g_new = max(0, x_g - 50)
    y_g_new = max(0, y_g - 50) 
    w_g_new = min(frameWidth, x_g + w_g + 50) - x_g_new 
    h_g_new = min(frameHeight, y_g + h_g + 50) - y_g_new  
    cv2.rectangle(res1, (x_g_new, y_g_new), (x_g_new + w_g_new, y_g_new + h_g_new), (255, 255, 0), 2)

    img_green = edges1[y_g_new:(y_g_new + h_g_new), x_g_new:(x_g_new + w_g_new)]

    # img_green=edges1[y_g:(y_g+h_g),x_g:(x_g+w_g)]


    # total_mask = cv2.bitwise_or(mask1, cv2.bitwise_or(mask2, mask3))
    # cv2.imshow("mask",total_mask)
    # edges[total_mask > 0] = [0]
    cv2.imshow("edges",edges)

    #################识别直线，不看颜色框里线，避免被物料直边干扰
    lines = cv2.HoughLines(edges,1,np.pi/180,threshold =150)
    cnt = 0
    sumTheta = 0
    averageTheta = 0
    # global last_theta
    last_theta = 0
    if lines is not None:
        for line in lines:
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
        averageTheta = 5.0 * sumTheta / cnt 
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

    #####################识别圆环
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
    if largest_circle_g is not None and largest_area_g > cutiao_center_circle*w*h:    #0.016
        (x, y), radius = cv2.minEnclosingCircle(largest_circle_g)
        x=x+x_g_new
        y=y+y_g_new
        center = (int(x), int(y))
        radius = int(radius)
        cv2.circle(res1, center, 2, (0, 0, 255), 3)
        cv2.circle(res1, center, radius, (0, 255, 0), 2)  
        # center_text = f"({center[0]}, {center[1]}), radius: {radius}"
        # text_position = (center[0] + 10, center[1] - 10)
        # area_text = f"Area: {largest_area_g}"
        # cv2.putText(res1, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        # cv2.putText(res1, area_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
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

    left=-6
    right=6 #6
    # print("left:",left,"right:",right)
    print("x_incolor:",x_incolor,"y_incolor:",y_incolor)
    print("detx1:",detx1,"dety1:",dety1)
    # if cutiaocishu % 2 ==0:
    #     left=-6
    #     right=6
    # else:
    #     left=-2
    #     right=6
    det=4
    if (x_incolor)<det and abs(y_incolor)<det:
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


def findCountours(camera_cap):  #/没在用/  findcontours灰度识别圆心
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


    gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)   #ת Ҷ ͼ
    equalized = cv2.equalizeHist(gray)
    # cv2.imshow("junheng",equalized)
    blurred = cv2.GaussianBlur(equalized, (9, 9), 2)
    edges = cv2.Canny(blurred, 50, 150)
    # circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 0.7,70,
    #                         param1=100, param2=150, minRadius=50, maxRadius=0)    #ʶ  Բ  
    flag = 0
    detx = 0 #     Ĳ  
    dety = 0
    detx1=0
    dety1=0

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)
    edges1 = cv2.Canny(closed, 50, 150)
    ret,erzhi=cv2.threshold(closed, 50, 255, cv2.THRESH_BINARY_INV)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    cv2.imshow("blu",binary)
    cv2.imshow("edges1",edges1)
    cv2.imshow("erzhi",erzhi)
    contours, _ = cv2.findContours(erzhi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    

#   ʼ      
    largest_circle = None
    largest_area = 0

    move_flag = 0
    stop_flag = 0


    for contour in contours:
    #              
    #          С    
        area = cv2.contourArea(contour)
        # print("area:",area)
        if area > largest_area:
            largest_area = area
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            if len(approx) > 3:  # Բ εĽ  ƶ   α   Ӧ ô   8
                largest_circle = approx
                # print("largest area:",largest_area)
                if largest_area > 10000 :
                    cv2.drawContours(res1, [largest_circle], 0, (0, 0, 255), 3)
                    #     Բ ĺͰ뾶
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
                    #     Բ
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


def findContours_ifgreen(camera_cap):  #/没在用/  圆环粗调 找绿色部分
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
    ##Բ   ж 
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

    # # ѭ       󣬸    largest_circle   ֵ         ߼ 
    # if largest_circle is not None and largest_area > 10000:
    #     (x, y), radius = cv2.minEnclosingCircle(largest_circle)
    #     center = (int(x), int(y))
    #     radius = int(radius)
    #     cv2.circle(res1, center, 2, (0, 0, 255), 3)  #     Բ  
    #     cv2.circle(res1, center, radius, (0, 255, 0), 2)  #        Բ
    #     center_text = f"({center[0]}, {center[1]}), radius: {radius}"
    #     text_position = (center[0] + 10, center[1] - 10)
    #     area_text = f"Area: {largest_area}"
    #     cv2.putText(res1, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    #     cv2.putText(res1, area_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    # else:
    #     cv2.putText(res1, 'No circle found', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
    ################
    ##  ɫ ж 
    red_min   = np.array([  0, 60,  60])
    red_max   = np.array([ 12, 203, 255])
    blue_min  = np.array([94,  50, 80])
    blue_max  = np.array([133, 230, 255])
    red_min1   = np.array([  155, 43,  46])
    red_max1   = np.array([ 180, 255, 255])

    hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV)
    mask12 = cv2.inRange(hsv,   red_min,   red_max)
    mask11 = cv2.inRange(hsv,   red_min1,   red_max1)
    mask1 = cv2.add(mask12,mask11)  #  ɫ    
    mask3 = cv2.inRange(hsv,  blue_min,  blue_max)   #  ɫ    
    # mask_not_red_blue = cv2.bitwise_not(src1,src1,mask_notgreen)
    # cv2.imshow("not green",mask_not_red_blue)
    #          еķ           
    red_pixels = cv2.countNonZero(mask1)
    blue_pixels = cv2.countNonZero(mask3)
    print("red_pixels:",red_pixels,"blue_pixels:",blue_pixels)
    #  Ҫ   ݾ     뿴   Ĵ С ټ һ  ʶ     ظ     Χ ж 
    color = None
    if red_pixels > blue_pixels:
        color = "Red"
    elif blue_pixels > red_pixels:
        color = "Blue"
    else:
        color = "Unknown"
    #      ɫ
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

        # ѭ       󣬸    largest_circle   ֵ         ߼ 
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
            cv2.circle(res1, center, 2, (0, 0, 255), 3)  #     Բ  
            cv2.circle(res1, center, radius, (0, 255, 0), 2)  #        Բ
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
    #         move_direction=1   #    
    #         move_distance = 11111
    #     elif x<(x_b+w_b):
    #         move_direction=2   #    
    #         move_distance = 11111
    else:
        if color == 'Red':
            move_direction=1   #    
            move_distance = 22222
        elif color == 'Blue':
            move_direction=2   #    
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
    

def circlePut1(cap):  #细调第二步 灰度houghcircles识别圆心
    # success, frame = cap.read()
    # success, frame = cap.read()
    success = cap.grab()
    success = cap.grab()
    success = cap.grab()
    success, frame = cap.read()
    # corrected_frame=undistortion(frame,mtx,dist)  # 图像去畸变（如果需要）
    # cv2.imshow("corrected",frame)
    src1 = frame.copy()
    res1 = src1.copy()
    # gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)  # 转换为灰度图
    # blurred = cv2.GaussianBlur(gray, (9, 9), 2)  # 高斯模糊
    # edges = cv2.Canny(blurred, 50, 150)  # Canny边缘检测
    h, w = res1.shape[:2]  # 获取图像的高度和宽度

    # 以下代码被注释，但保留用于参考
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))  # 定义结构元素
    # opened = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)  # 闭运算
    # closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)  # 闭运算
    # closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)  # 闭运算
    # edges1 = cv2.Canny(blurred, 50, 150)  # Canny边缘检测
    # cv2.imshow("closed",closed)
    # cv2.imshow("edges1",edges1)

    # ret, thresh = cv2.threshold(closed, 200, 255, cv2.THRESH_BINARY_INV)  # 二值化
    # adaptive_thresh = cv2.adaptiveThreshold(closed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                                        cv2.THRESH_BINARY, 11, 2)  # 自适应阈值
    # edgead=cv2.Canny(adaptive_thresh,50,200)  # Canny边缘检测
    # cv2.imshow('Adaptive Threshold', adaptive_thresh)
    # cv2.imshow('adedge',edgead)
    # cv2.imshow('edges',edges)
    # cv2.imshow('edges1',edges1)
    # cv2.imshow('gray',gray)

    # 转换为灰度图并进行直方图均衡化
    gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)   
    # cv2.imshow("gray",gray)
    equalized = cv2.equalizeHist(gray)  # 直方图均衡化
    gamma=0.5
    invgamma = 1/gamma
    gamma_image = np.array(np.power((gray/255), invgamma)*255, dtype=np.uint8)
    # # equalized = cv2.equalizeHist(gamma_image)
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # enhanced = clahe.apply(gray)    
    # cv2.imshow("junheng",equalized)
    cv2.imshow("gamma",gamma_image)
    # cv2.imshow("enhanced",enhanced)
    

    # 形态学运算和高斯模糊
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))  # 定义结构元素
    # opened = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)  # 闭运算
    # closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)  # 闭运算
    # blurred = cv2.GaussianBlur(closed1, (9, 9), 2)  # 高斯模糊
    blurred1 = cv2.GaussianBlur(gamma_image, (9, 9), 2)  # 高斯模糊
    # blu_equ=cv2.equalizeHist(blurred1)
    
    # cv2.imshow("blu_equ",blu_equ)
    # edges = cv2.Canny(blurred, 50, 150)  # Canny边缘检测
    # cv2.imshow("xitiaoedge:",edges)11
    # 忽略 x < 150 范围的图像
    blurred1[:, :200] = 0  # 将 x < 150 的部分设置为黑色
    # 忽略 1160 < x < 1280 范围的图像
    blurred1[:, 1160:1280] = 0  # 将 1160 < x < 1280 的部分设置为黑色
    cv2.imshow("blurred1",blurred1)

    # 使用HoughCircles检测圆
    circles = cv2.HoughCircles(blurred1, cv2.HOUGH_GRADIENT, 0.7, 70,
                            param1=100, param2=83, minRadius=houghradius_min, maxRadius=houghradius_max)    # 5th circle
    
    #640/480------140/155   
    #minradius 124  param2:65 param1:100  128
    # circles = cv2.HoughCircles(blurred1, cv2.HOUGH_GRADIENT, 0.7,70,
    #                         param1=100, param2=52, minRadius=houghradius_min_6th, maxRadius=houghradius_max_6th)    #6th circle

    # 如果检测到圆
    # flag = 0  # 初始化标志位
    detx = 0  # 初始化xy方向偏差
    dety = 0  
    detx1 = 10000  # 初始化xy方向偏差（用于判断是否检测到圆）
    dety1 = 10000  
    radius=0
    largest_circle = None  # 初始化最大圆
    stop_flag = 0  # 初始化停止标志
    if circles is not None:
        flag = 1  # 检测到圆，设置标志位
        circles = np.uint16(np.around(circles))  # 转换为整数
        for i in circles[0, :]:  # 遍历检测到的圆
            if largest_circle is None or i[2] > largest_circle[2]:  # 找到最大的圆
                largest_circle = i 

        # 如果找到最大圆
        if largest_circle is not None:
            # # 绘制圆心和圆
            cv2.circle(res1, (largest_circle[0], largest_circle[1]), largest_circle[2], (0, 0, 255), 2)
            cv2.circle(res1, (largest_circle[0], largest_circle[1]), 2, (0, 0, 255), 3)
            # center_text = f"({largest_circle[0]}, {largest_circle[1]})"  # 圆心坐标
            # text_position = (largest_circle[0] + 10, largest_circle[1] - 10)  
            # cv2.putText(res1, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            radius = largest_circle[2]  # 圆的半径
            radius_text = f"Radius: {radius}"  # 半径文本
            radius_position = (largest_circle[0] + 10, largest_circle[1] + 20)  
            cv2.putText(res1, radius_text, radius_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            # 计算偏差
            detx = largest_circle[0] - w/2 - correct_x_hough
            dety = h/2 - largest_circle[1] - correct_y_hough
            detx1 = int(round(detx))  # 四舍五入
            dety1 = int(round(dety))  
            print("detx=", detx, "dety=", dety)
            # print("detx1=",detx1,"dety1=",dety1)
            # pi=math.pi
            # area=largest_circle[2]*largest_circle[2]*pi
            # area_text=f"{area}"
            # cv2.putText(res1, area_text, (largest_circle[0], largest_circle[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    else:
        # 如果未检测到圆，显示提示信息
        cv2.putText(res1, 'no', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    # 显示结果
    cv2.imshow("2", res1)
    # 判断是否停止
    if abs(detx) < 4 and abs(dety) < 4:
        stop_flag = 1
    # 如果未检测到圆，重置偏差（此时停止标志位stop_flag仍为0，未到位
    if (detx1 == 10000) and (dety1 == 10000):
        stop_flag=0
        detx1 = 0
        dety1 = 0
    print("radius:",radius,"detx1=", detx1, "dety1=", dety1, "stop_flag:", stop_flag)
    cv2.waitKey(1)
    return detx1, dety1, stop_flag

def circlePut_color(color_cap,color_number):  #细调第一步 颜色画框确保第五环能被看见
    red_min   =  np.array(dim_red_min)
    red_max   =  np.array(dim_red_max)
    green_min =  np.array(dim_green_min)
    green_max =  np.array(dim_green_max)
    blue_min  =  np.array(dim_blue_min)   
    blue_max  =  np.array(dim_blue_max)  
    red_min1   = np.array(dim_red_min1)  
    red_max1   = np.array(dim_red_max1)
    # ret = color_cap.grab()
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret,frame = color_cap.read()

    src1 = frame.copy()
    res1 = src1.copy()
    hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV) 
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
    # cv2.imshow("res1",res1)

    h, w = res1.shape[:2]
    # blured = cv2.blur(res1, (7, 7))
    blured = cv2.blur(res1, (5, 5))
    ret, bright = cv2.threshold(blured, 10, 255, cv2.THRESH_BINARY)
    
    gray = cv2.cvtColor(bright, cv2.COLOR_BGR2GRAY)
    # h_g, w_g = gray.shape[:2]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)


    x_center = 0
    y_center = 0
    # c = 0
    detx_p=10000
    dety_p=10000
    flag_color_1 = 0
    cv2.imshow("closed",closed)

    c=4e-4
    #blue
    x_b=0
    y_b=0
    w_b=0
    h_b=0
    contours_, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    large_contours_ = []
    for contour in contours_:
        area = cv2.contourArea(contour)
        if area > 400 :
            large_contours_.append(contour)
            x_b1, y_b1, w_b1, h_b1 = cv2.boundingRect(contour)
            cv2.rectangle(src1, (x_b1, y_b1), (x_b1 + w_b1, y_b1 + h_b1), (0, 0, 255), 2)
    if large_contours_:
        merged_contour_b = np.vstack(large_contours_)
        x_b, y_b, w_b, h_b = cv2.boundingRect(merged_contour_b)
        cv2.rectangle(src1, (x_b, y_b), (x_b + w_b, y_b + h_b), (255, 0, 0), 2)
        a = x_b + w_b / 2
        b = y_b + h_b / 2
        detx_p = a - w/2 - correct_x_hough
        dety_p = h/2 - correct_y_hough - b
        detx_p = int(detx_p)
        dety_p = int(dety_p)


    # contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # for contour in contours:
    #     area = cv2.contourArea(contour)
    #     # print("area:",area)
    #     if area > largest_area:
    #         largest_area = area
    #         largest=contour
    # if largest is not None and largest_area > 47000: 
    #     (x1, y1, w1, h1) = cv2.boundingRect(largest)
    #     a = x1 + w1 / 2
    #     b = y1 + h1 / 2
    #     cv2.rectangle(src1, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2) 
    #     cv2.putText(src1, 'color', (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    #     # area_text=f"{area}"
    #     area_text=f"{w1*h1}"
    #     cv2.putText(src1, area_text, (x1+60, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    #     center_text = f"({a}, {b})"
    #     cv2.putText(src1, center_text, (x1, y1+h1+5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    #     color_text=f"{color_number}"
    #     cv2.putText(src1, color_text, (x1, y1+h1+10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    #     detx_p = a - w/2 - correct_x_hough
    #     dety_p = h/2 - correct_y_hough - b
    #     detx_p = int(detx_p)
    #     dety_p = int(dety_p)
    #     # print("detx_p:",detx_p,"dety_p:",dety_p)
    if abs(detx_p)<6 and abs(dety_p)<6:
        flag_color_1 =1
    if (detx_p==10000) and (dety_p==10000):
        detx_p=0
        dety_p=0
    cv2.imshow("src1",src1)
    print("detx_p:",detx_p,"dety_p:",dety_p,"flag_color_1:",flag_color_1)
    cv2.waitKey(1)
    return x_center/ w,y_center/h,frame,flag_color_1,detx_p,dety_p

def findGoodsCenter(color_cap,color_number):  #爪子夹不紧时 识别所抓物料中心值
    flag_color_1 = 0
    # color_number = 0
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
    
    # y0,x0 = frame.shape[:2]
    # frame_change = cv2.resize(frame, (int(x0), int(y0)))

    src1 = frame.copy()
    res1 = src1.copy()
    hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV)   
    mask0=None
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
    # blured = cv2.blur(res1, (7, 7))
    blured = cv2.blur(res1, (5, 5))
    ret, bright = cv2.threshold(blured, 10, 255, cv2.THRESH_BINARY)
    
    gray = cv2.cvtColor(bright, cv2.COLOR_BGR2GRAY)
    h_g, w_g = gray.shape[:2]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)

    contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    num = 0
    # a_sum=0
    # b_sum=0
    x_center = 0
    y_center = 0
    c = 0
    detx=10000
    dety=10000
    detx_p=0
    dety_p=0
    #左上 460 140    右下 910 540？？？
    for cnt343 in contours:
        (x1, y1, w1, h1) = cv2.boundingRect(cnt343)  
        area = cv2.contourArea(cnt343)
        if w1*h1 > 0.05*w*h:
        # if area > 0.07*w*h:
            peri = cv2.arcLength(cnt343, True)
            approx = cv2.approxPolyDP(cnt343, 0.02 * peri, True)
            cv2.drawContours(src1, [approx], 0, (0, 0, 255), 3)
            (x, y), radius = cv2.minEnclosingCircle(approx)
            center = (int(x), int(y))
            radius = int(radius) 
            cv2.circle(src1, center, 2, (0, 0, 255), 3)
            cv2.circle(src1, center, radius, (0, 255, 0), 2)
            a = x1 + w1 / 2
            b = y1 + h1 / 2
            # a_sum +=a
            # b_sum +=b
            num += 1
            # area_text=f"{w1*h1}"
            # cv2.putText(src1, area_text, (x1+60, y1 +h1+ 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if num == 1 or c < y1:
                x_center = a
                y_center = b
                c = y1
            # x_center=int(round(x))
            # y_center=int(round(y))
            flag_color_1 = 1
            detx = x - w/2 
            dety = h/2 - y
            detx_p = int(round(detx))
            dety_p = int(round(dety))
            print("detx:",detx,"dety:",dety)
    cv2.imshow("src1",src1)
    cv2.waitKey(1)
    return x_center,y_center,flag_color_1,detx_p,dety_p

def updateCorrectxy(color_cap,color_number):   #爪子夹不紧时 更新中心位置偏差值
    detx_,dety_,flag_=0,0,0
    for i in range(3):
        x_update,y_update,flag_update,detx_update,dety_update=findGoodsCenter(color_cap,color_number)
        if flag_update==1:
            detx_+=detx_update
            dety_+=dety_update
            flag_+=flag_update
    detx_ave=detx_/flag_
    dety_ave=dety_/flag_
    global correct_x_hough
    global correct_y_hough
    correct_x_hough=detx_ave
    correct_y_hough=dety_ave
    print("correct_x_update:",correct_x_hough,"correct_y_update",correct_y_hough)
    return 0

def defaltCorrectxy():
    global correct_x_hough
    global correct_y_hough
    correct_x_hough=correct_x_hough_default
    correct_y_hough=correct_y_hough_default



def findBlockCenter_get(color_cap):  #一排三个处夹取（不在转盘
    flag_color_1 = 0
    color_number = 0
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
    
    # y0,x0 = frame.shape[:2]
    # frame_change = cv2.resize(frame, (int(x0), int(y0)))

    src1 = frame.copy()
    res1 = src1.copy()
    hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV)   

    mask12 = cv2.inRange(hsv,   red_min,   red_max)
    mask11 = cv2.inRange(hsv,   red_min1,   red_max1)
    mask2 = cv2.inRange(hsv, green_min, green_max)
    mask3 = cv2.inRange(hsv,  blue_min,  blue_max)
    mask1 = cv2.add(mask12,mask11)

    red_pixels = cv2.countNonZero(mask1)
    green_pixels = cv2.countNonZero(mask2)
    blue_pixels = cv2.countNonZero(mask3)
    print("red_pixels:",red_pixels,"green_pixels",green_pixels,"blue_pixels:",blue_pixels)
    color = None
    if red_pixels > blue_pixels and red_pixels > green_pixels:
        color_number = 1
    elif green_pixels > red_pixels and green_pixels > blue_pixels:
        color_number = 2
    elif blue_pixels > red_pixels and blue_pixels > green_pixels:
        color_number = 3

    if color_number == 1:
        mask0 = mask1
    elif color_number == 2:
        mask0 = mask2
    elif color_number == 3:
        mask0 = mask3
    res1 = cv2.bitwise_and(src1, src1, mask=mask0)   
    cv2.imshow("res1",res1)

    h, w = res1.shape[:2]
    blured = cv2.blur(res1, (7, 7))# ˲ 
    blured = cv2.blur(res1, (5, 5))
    ret, bright = cv2.threshold(blured, 10, 255, cv2.THRESH_BINARY)#  ֵ  
    
    gray = cv2.cvtColor(bright, cv2.COLOR_BGR2GRAY)
    h_g, w_g = gray.shape[:2]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)#      
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)

    contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)#          ڻ ȡɫ 鷶Χ
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
    detx=10000
    dety=10000
    detx_p=0
    dety_p=0
    for cnt343 in contours:
        (x1, y1, w1, h1) = cv2.boundingRect(cnt343)  
        area = cv2.contourArea(cnt343)
        if w1*h1 > 0.016*w*h:
        # if area > 0.07*w*h:
            a = x1 + w1 / 2
            b = y1 + h1 / 2
            a_sum +=a
            b_sum +=b
            num += 1
            # print("color",num,":",a/w, b/h)
            # s=(x1+w1)*(y1+h1)
            
            cv2.rectangle(src1, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2)
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
            # flag_color_1 = 1
            detx = a - w/2 - correct_x_hough
            dety = h/2 - correct_y_hough - b
            detx_p = int(detx)
            dety_p = int(dety)
            print("detx:",detx,"dety:",dety)
    if abs(detx)<12 and abs(dety)<12:
        flag_color_1=1
    if detx==10000 and dety==10000:
        detx_p=0
        dety_p=0
        flag_color_1=0
    cv2.imshow("src1",src1)
    cv2.waitKey(1)
    return x_center/ w,y_center/h,frame,flag_color_1,detx_p,dety_p,color_number


def findBlockCenter(color_cap,color_number):   #转盘处识别色块中心位置
    flag_color_1 = 0   #是否识别到物料标志位
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

    src1 = frame.copy()
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
    # blured = cv2.blur(res1, (7, 7))
    blured = cv2.blur(res1, (5, 5))
    ret, bright = cv2.threshold(blured, 10, 255, cv2.THRESH_BINARY)
    gray = cv2.cvtColor(bright, cv2.COLOR_BGR2GRAY)
    h_g, w_g = gray.shape[:2]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)

    contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    num = 0
    x_center = 0
    y_center = 0
    x_t,y_t,w_t,h_t=0,0,0,0
    # c = 0
    c=float('inf')
    detx_p=0
    dety_p=0
    for cnt343 in contours:
        (x1, y1, w1, h1) = cv2.boundingRect(cnt343)  
        area = cv2.contourArea(cnt343)
        # print("area:",w1*h1)
        # cv2.rectangle(src1, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0), 2)  
        # area_text=f"{w1*h1}"
        # cv2.putText(src1, area_text, (x1+60, y1 +h1+ 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        if w1*h1 > block_area*w*h:    #0.039
        # if area > 0.07*w*h:
            # print("success:",w1*h1)
            a = x1 + w1 / 2
            b = y1 + h1 / 2
            num += 1
            # print("color",num,":",a/w, b/h)
            # s=(x1+w1)*(y1+h1)
            
            cv2.rectangle(src1, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2) 
            # cv2.putText(src1, 'color', (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            # # area_text=f"{area}"
            # area_text=f"{w1*h1}"
            # cv2.putText(src1, area_text, (x1+60, y1 +h1+ 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            # center_text = f"({a}, {b})"
            # cv2.putText(src1, center_text, (x1, y1+h1+5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            # color_text=f"{color_number}"
            # cv2.putText(src1, color_text, (x1, y1+h1+10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            
            # if num == 1 or c < y1:
            #     x_center = a
            #     y_center = b
            #     c = y1
            # flag_color_1 = 1
            # detx_p = a - w/2 - correct_x_hough
            # dety_p = h/2 - correct_y_hough - b
            # detx_p = int(detx_p)
            # dety_p = int(dety_p)

            if num == 1 or y1 < c:
                x_center = a
                y_center = b
                c = y1
                x_t,y_t,w_t,h_t=x1, y1, w1, h1
            # flag_color_1 = 1
            # detx_p = a - w/2 - correct_x_hough
            # dety_p = h/2 - correct_y_hough - b
            # detx_p = int(detx_p)
            # dety_p = int(dety_p)
    if c != float('inf'):  # 确保找到了至少一个符合条件的色块
        # x1 = int(x_center - w1 / 2)
        # y1 = int(y_center - h1 / 2)
        # cv2.rectangle(src1, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 255), 2)  # 使用红色框表示最上方的色块
        cv2.rectangle(src1, (x_t, y_t), (x_t + w_t, y_t + h_t), (255, 0, 255), 2)  # 画出最上方的色块
        # # cv2.putText(src1, "Topmost Block", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)  # 添加文字标记
        x_center = x_t + w_t / 2
        y_center = y_t + h_t / 2
        flag_color_1 = 1
        detx_p = x_center - w/2 - correct_x_hough
        dety_p = h/2 - correct_y_hough - y_center
        detx_p = int(detx_p)
        dety_p = int(dety_p)

    print("detx_p:",detx_p,"dety_p:",dety_p,"flag_color_1:",flag_color_1)
    cv2.imshow("src1",src1)
    cv2.waitKey(1)
    return x_center/ w,y_center/h,frame,flag_color_1,detx_p,dety_p

def findBlockCenter_gray(color_cap):   #在转盘上放物料（转盘上是色块（一直调整位置直到到中心值
    color_number=0
    flag_color_1 = 0
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret,frame = color_cap.read()

    src1 = frame.copy()
    res1 = src1.copy()
    h, w = res1.shape[:2]
    # hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV)
    cv2.imshow("res1",res1)

    # gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)   
    # # equalized = cv2.equalizeHist(gray)  # 直方图均衡化
    # gamma=0.5
    # invgamma = 1/gamma
    # gamma_image = np.array(np.power((gray/255), invgamma)*255, dtype=np.uint8)
    # cv2.imshow("gamma",gamma_image)
    # blurred1 = cv2.GaussianBlur(gamma_image, (9, 9), 2)  # 高斯模糊
    # circles = cv2.HoughCircles(blurred1, cv2.HOUGH_GRADIENT, 0.7,70,
    #                         param1=100, param2=65, minRadius=houghradius_min, maxRadius=houghradius_max)    #5th circle


    # #124 155
    # x=0
    # y=0
    # detx = 0 
    # dety = 0
    # detx1 = 0
    # dety1 = 0
    # largest_circle = None  
    # stop_flag=0
    # if circles is not None:
    #     flag = 1
    #     circles = np.uint16(np.around(circles))
    #     for i in circles[0, :]:
    #         if largest_circle is None or i[2] > largest_circle[2]:
    #             largest_circle = i  


    #     if largest_circle is not None:
    #         x=largest_circle[0]
    #         y=largest_circle[1]
    #         cv2.circle(res1, (largest_circle[0], largest_circle[1]), largest_circle[2], (0, 0, 255), 2)
    #         cv2.circle(res1, (largest_circle[0], largest_circle[1]), 2, (0, 0, 255), 3)
    #         # center_text = f"({largest_circle[0]}, {largest_circle[1]})"
    #         # text_position = (largest_circle[0] + 10, largest_circle[1] - 10)
    #         # cv2.putText(edges, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    #         # radius = largest_circle[2]
    #         # radius_text = f"Radius: {radius}"
    #         # radius_position = (largest_circle[0] + 10, largest_circle[1] + 20) 
    #         # cv2.putText(res1, radius_text, radius_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    #         detx = largest_circle[0] - w/2 -correct_x_hough
    #         dety = h/2 - largest_circle[1] -correct_y_hough
    #         detx1 = int(round(detx))
    #         dety1 = int(round(dety))
    #         flag_color_1 = 1
    #         # print("detx=",detx,"dety=",dety)
    #         print("detx1=",detx1,"dety1=",dety1)
    # else:
    #     cv2.putText(res1, 'no', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # cv2.imshow("res1",res1)
    # cv2.waitKey(1)

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
    # blured = cv2.blur(res1, (7, 7))# ˲ 
    # blured = cv2.blur(res1, (5, 5))
    # ret, bright = cv2.threshold(blured, 10, 255, cv2.THRESH_BINARY)#  ֵ  
    
    # gray = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)
    # h_g, w_g = gray.shape[:2]
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    # opened = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)#      
    # closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    # closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)
    # cv2.imshow("closed",closed)

    # contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)#          ڻ ȡɫ 鷶Χ
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
    #     (x1, y1, w1, h1) = cv2.boundingRect(cnt343)  #  ú      ؾ    ĸ   
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
            
    #         cv2.rectangle(src1, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2)  #     ⵽    ɫ      
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


    gray = cv2.cvtColor(src1, cv2.COLOR_BGR2GRAY)   #ת Ҷ ͼ
    equalized = cv2.equalizeHist(gray)
    # cv2.imshow("junheng",equalized)
    blurred = cv2.GaussianBlur(equalized, (9, 9), 2)
    detx = 0 #     Ĳ  
    dety = 0
    detx1=0
    dety1=0

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)
    edges1 = cv2.Canny(blurred, 50, 150)
    cv2.imshow("blu",blurred)
    cv2.imshow("edges1",edges1)
    edges1 = cv2.Canny(blurred, 50, 150)
    cv2.imshow("blu",blurred)
    ###############cv2.imshow("edges1",edges1)
    contours, _ = cv2.findContours(edges1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   
    largest_circle = None
    largest_area = 0

    move_flag = 0
    stop_flag = 0
    x=0
    y=0

    for contour in contours:
    #              
    #          С    
        area = cv2.contourArea(contour)
        # print("area:",area)
        if area > largest_area:
            largest_area = area
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            if len(approx) > 5:  # Բ εĽ  ƶ   α   Ӧ ô   8
                largest_circle = approx
                # print("largest area:",largest_area)
    if largest_area > 10000 and largest_circle is not None:
        cv2.drawContours(res1, [largest_circle], 0, (0, 0, 255), 3)
        #     Բ ĺͰ뾶
        (x, y), radius = cv2.minEnclosingCircle(largest_circle)
        # print("x=",x,"y=",y)
        center = (int(x), int(y))
        radius = int(radius)
        detx = x - w/2 - correct_x_hough
        dety = h/2 - correct_y_hough - y
        # print("detx=",detx,"dety=",dety)
        detx1 = int(round(detx))
        dety1 = int(round(dety))
        cv2.circle(res1, center, 2, (0, 0, 255), 3)
        #     Բ
        cv2.circle(res1, center, radius, (0, 255, 0), 2)
        center_text = f"({center[0]}, {center[1]}), radius: {radius}"
        text_position = (center[0] + 10, center[1] - 10)
        area_text=f"({largest_area})"
        cv2.putText(res1, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.putText(res1, area_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        # print('  detx1:',detx1,'  dety1:',dety1)

        flag_color_1 = 1
    
    return x/w,y/h,frame,flag_color_1,detx1,dety1,color_number

def findBlockCenter_circle(color_cap,color_number):   #在转盘上放物料（转盘上是圆环（在每个圆环处夹着物料调整并放置
    red_min   =  np.array(dim_red_min)
    red_max   =  np.array(dim_red_max)
    green_min =  np.array(dim_green_min)
    green_max =  np.array(dim_green_max)
    blue_min  =  np.array(dim_blue_min)   
    blue_max  =  np.array(dim_blue_max)  
    red_min1   = np.array(dim_red_min1)  
    red_max1   = np.array(dim_red_max1)
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret,frame = color_cap.read()

    src1 = frame.copy()
    res1 = src1.copy()
    hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV) 
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
    blured = cv2.blur(res1, (7, 7))
    blured = cv2.blur(res1, (5, 5))
    ret, bright = cv2.threshold(blured, 10, 255, cv2.THRESH_BINARY)
    
    gray = cv2.cvtColor(bright, cv2.COLOR_BGR2GRAY)
    equalized = cv2.equalizeHist(gray)
    h_g, w_g = gray.shape[:2]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)
    blurred1 = cv2.GaussianBlur(equalized, (9, 9), 2)
    # cv2.imshow("junheng",blurred)
    # edges = cv2.Canny(blurred, 50, 150)
    # cv2.imshow("xitiaoedge:",edges)

    circles = cv2.HoughCircles(blurred1, cv2.HOUGH_GRADIENT, 0.7,70,
                            param1=100, param2=65, minRadius=houghradius_min, maxRadius=houghradius_max)    #5th circle
    # circles = cv2.HoughCircles(blurred1, cv2.HOUGH_GRADIENT, 0.7,70,
    #                         param1=100, param2=35, minRadius=houghradius_min_6th, maxRadius=houghradius_max_6th)    #6th circle
    flag = 0
    detx = 0 
    dety = 0
    detx1 = 0
    dety1 = 0
    x_center=0
    y_center=0
    flag_color_1=0
    largest_circle = None  #    ڴ洢   Բ    Ϣ
    stop_flag=0
    if circles is not None:
        flag = 1
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            if largest_circle is None or i[2] > largest_circle[2]:
                largest_circle = i 


        if largest_circle is not None:
            x_center=largest_circle[0]
            y_center=largest_circle[1]
            cv2.circle(src1, (largest_circle[0], largest_circle[1]), largest_circle[2], (0, 0, 255), 2)
            cv2.circle(src1, (largest_circle[0], largest_circle[1]), 2, (0, 0, 255), 3)
            center_text = f"({largest_circle[0]}, {largest_circle[1]})"
            text_position = (largest_circle[0] + 10, largest_circle[1] - 10)
            # cv2.putText(edges, center_text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            radius = largest_circle[2]
            radius_text = f"Radius: {radius}"
            radius_position = (largest_circle[0] + 10, largest_circle[1] + 20) 
            cv2.putText(src1, radius_text, radius_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            detx = largest_circle[0] - w/2 -correct_x_hough
            dety = h/2 - largest_circle[1] -correct_y_hough
            detx1 = int(round(detx))
            dety1 = int(round(dety))
            flag_color_1 = 1
            # print("detx=",detx,"dety=",dety)
            # print("detx1=",detx1,"dety1=",dety1)
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



    # contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)#          ڻ ȡɫ 鷶Χ
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
    # #              
    # #          С    
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
    #     cv2.rectangle(src1, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2)  #     ⵽    ɫ      
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

def detectPlate(camera_cap,color_number):   #检测转盘是否停止（从转盘上夹走物料
    # success, frame = camera_cap.read()
    global turn_direction
    cnt2 = 0
    x_add = 0
    y_add = 0
    get_blog = 0
    flag_stop = 0
    times=4   #6
    while(cnt2 < times):
        
        global x_,y_
        x_,y_,img_,flag_,detx_,dety_= findBlockCenter(camera_cap,color_number)
        x_add = x_add + x_
        y_add = y_add + y_
        # cv2.imshow("img",img_)
        cv2.waitKey(1)
        # time.sleep(8e-2)
        cnt2 = cnt2 + 1
        get_blog = get_blog +flag_
    x_add = x_add /times
    y_add = y_add /times
    # print("get_blog",get_blog)
    if (abs(x_ - x_add) <0.01 and abs(y_ - y_add) < 0.01 and get_blog == times): 
        flag_stop=1
    else:
        # if get_blog == times:
        #     if((x_ - x_add)>0.02 ):
        #         turn_direction = True
        #     if((x_ - x_add)<-0.02 ):
        #         turn_direction = False
        flag_stop=0 
    print("flag:",flag_stop)
    cv2.waitKey(1)
    return flag_stop

def detectPlate_check(camera_cap,color_number):  #夹第一个物料时检测爪子是否成功抓起
    # success, frame = camera_cap.read() 
    # global turn_direction
    cnt2 = 0
    get_blog = 0
    flag_stop = 0
    x_add = 0
    y_add = 0
    times = 3
    while(cnt2 < times): 
        
        global x_,y_
        x_,y_,img_,flag_,detx,dety= findBlockCenter(camera_cap,color_number)
        print("x_:",x_,"y_:",y_,"flag_:",flag_)
        # cv2.imshow("img",img_)
        cv2.waitKey(1)
        # time.sleep(8e-2)
        cnt2 = cnt2 + 1
        x_add = x_add + x_
        y_add = y_add + y_
        get_blog = get_blog +flag_
    x_add = x_add /times
    y_add = y_add /times
    if (abs(x_add-x_) <0.1 and abs(y_add-y_) < 0.1 and get_blog == times):  
        flag_stop=1
    print("get_blog",get_blog,"flag:",flag_stop)
    cv2.waitKey(1)
    return flag_stop

def detectPlate_gray(camera_cap):  #检测转盘是否停止（在转盘上放物料（转盘上是色块
    success, frame = camera_cap.read()  
    global turn_direction
    cnt2 = 0
    x_add = 0
    y_add = 0
    get_blog = 0
    flag_stop = 0
    times=5
    while(cnt2 < times): 
        
        global x_,y_
        x_,y_,img_,flag_,detx_,dety_,color_number= findBlockCenter_gray(camera_cap)
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
        flag_stop=1
    else:
        if get_blog == times:
            if((x_ - x_add)>0.02 ):
                turn_direction = True
            if((x_ - x_add)<-0.02 ):
                turn_direction = False
        flag_stop=0 
    print("zhuanpantingzhi flag:",flag_stop)
    cv2.waitKey(1)
    return flag_stop

def detectPlate_circle(camera_cap,color_number):   #检测转盘是否停止（在转盘上放物料（转盘上是圆环
    success, frame = camera_cap.read()  
    global turn_direction
    cnt2 = 0
    x_add = 0
    y_add = 0
    get_blog = 0
    flag_stop = 0
    times=3
    while(cnt2 < times): 
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
    # print("gray_getblog:",get_blog)
    # print("get_blog",get_blog)
    if (abs(x_ - x_add) <0.01 and abs(y_ - y_add) < 0.01 and get_blog == times): 
        flag_stop=1
    else:
        if get_blog == times:
            if((x_ - x_add)>0.02 ):
                turn_direction = True
            if((x_ - x_add)<-0.02 ):
                turn_direction = False
        flag_stop=0 
    print("zhuanpantingzhi flag:",flag_stop)
    cv2.waitKey(1)
    return flag_stop

def detectLine(cap):   #直线检测
    ret=cap.grab()
    ret=cap.grab()
    ret=cap.grab()
    ret,frame = cap.read()

    cnt_line = 0
    res1=frame.copy()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   #ת Ҷ ͼ
    equalized = cv2.equalizeHist(gray)
    # cv2.imshow("junheng",equalized)
    # ret, thresh = cv2.threshold(equalized, 120, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(equalized, cv2.MORPH_CLOSE, kernel)#      
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    # closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)
    blurred = cv2.GaussianBlur(closed1, (9, 9), 2)
    edges = cv2.Canny(blurred, 50, 150)
    cv2.imshow("edges",edges)

    lines = cv2.HoughLines(edges,1,np.pi/180,threshold =150)#  ȡͼ е   
    cnt = 0
    sumTheta = 0
    averageTheta = 0
    # global last_theta
    last_theta = 0
    if lines is not None:
        for line in lines:#  ÿ   ߻     
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

    # cnt = 0
    # sumTheta = 0
    # averageTheta = 0
    # # global last_theta
    # last_theta = 0

    # lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=150, minLineLength=250, maxLineGap=80)
    # if lines is not None:
    #     for line in lines:
    #         x1, y1, x2, y2 = line[0]
            
    #         # 计算线段的角度
    #         if x2 != x1:  # 避免除以零
    #             theta = np.arctan2(y2 - y1, x2 - x1)
    #         else:
    #             theta = np.pi / 2  # 垂直线，角度为 90 度（π/2 弧度）
            
    #         # 筛选角度在 1.1 到 2.2 弧度之间的线段
    #         if 1.1 <= np.abs(theta) <= 2.2:
    #             cnt += 1
    #             sumTheta += theta / 5.0  # 或者直接加上 theta，取决于你的需求
                
    #             # 绘制线段
    #             cv2.line(res1, (x1, y1), (x2, y2), (0, 0, 255), 2)

    if not (cnt == 0):
        averageTheta = 5.0 * sumTheta / cnt #  ýǶȵ ƽ  ֵ
        # averageTheta = sumTheta / cnt
        last_theta =  averageTheta
    else :
        averageTheta = last_theta
    # print(averageTheta)
    averageTheta180=np.degrees(averageTheta)
    finaltheta=90-averageTheta180
    print("hudu:",averageTheta,"   jiaodu:",averageTheta180,"    jiajiao;",finaltheta)
    cv2.imshow("line",res1)
    line_flag=0
    if abs(finaltheta)<0.5:
    # if abs(finaltheta)<1:
        line_flag=1
    finaltheta=int(round(finaltheta))
    if (finaltheta==90 ):
        finaltheta=0
    cv2.waitKey(1)
    return finaltheta,line_flag


def detectLine_gray(color_cap):   #直线检测（黄灰交界线
    gray_min = np.array(dim_gray_min)
    gray_max = np.array(dim_gray_max)

    ret = color_cap.grab()
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret,frame = color_cap.read()

    
    # y0,x0 = frame.shape[:2]
    # frame_change = cv2.resize(frame, (int(x0), int(y0)))

    src1 = frame.copy()
    res1 = src1.copy()
    hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV)    
    mask_gray = cv2.inRange(hsv,   gray_min,   gray_max)

    res1 = cv2.bitwise_and(src1, src1, mask=mask_gray)   
    cv2.imshow("res1",res1)

    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   
    # equalized = cv2.equalizeHist(gray)
    # cv2.imshow("junheng",equalized)
    # ret, thresh = cv2.threshold(equalized, 120, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(res1, cv2.MORPH_CLOSE, kernel)
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    # closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)
    blurred = cv2.GaussianBlur(closed1, (9, 9), 2)
    edges = cv2.Canny(blurred, 50, 150)
    cv2.imshow("edges",edges)

    lines = cv2.HoughLines(edges,1,np.pi/180,threshold =120)
    cnt = 0
    sumTheta = 0
    averageTheta = 0
    # global last_theta
    last_theta = 0
    if lines is not None:
        for line in lines:
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
                cv2.line(frame,(x1,y1),(x2,y2),(0,0,255),2)
    if not (cnt == 0):
        averageTheta = 5.0 * sumTheta / cnt 
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

def code(code_cap):  #识别二维码、条形码
    ret,frame = code_cap.read()
    ret,frame = code_cap.read()
    ret,frame = code_cap.read()
    if code_cap.isOpened():
        print("222     successsssssssss")
    else:
        print("222     faillllllllll")
    count=0
    while ret == False and count<10:
        print("ret  fail")
        ret,frame = code_cap.read()
        count+=1
    cv2.imshow("frame",frame)
    barcodes = decode(frame)  
    flag = 0
    data = []
    # cv2.waitKey(10)

    
    for barcode in barcodes:
        #rect = barcode.rect
        #x, y, w, h = rect
        #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        data = barcode.data.decode("utf8")
        print(data)
        #cv2.putText(frame, data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        #print("Result:" + data)
    if len(barcodes)>0:
        flag = 1
    return data,flag

def sort(data):  #将二维码信息字符转为数字数组
    color_order = []
    print(data,type(data))
    for i in data:
        if ( i == '1'):
            color_order.append(1)
        elif ( i == '2'):
            color_order.append(2)
        elif ( i == '3'):
            color_order.append(3)
    return color_order



# def undistortion(img, mtx, dist):   #摄像头畸变校正
#     h, w = img.shape[:2]
#     newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

#     # print('roi ', roi)

#     dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

#     # crop the image
#     x, y, w, h = roi
#     if roi != (0, 0, 0, 0):
#         dst = dst[y:y + h, x:x + w]

#     return dst
