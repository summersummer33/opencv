import cv2
import numpy as np
import time
# import uvc
import testdef


# #��������ͷ��������
# capture_width = 640   #
# capture_height = 480
framerate = 60			# ֡��

# cap = cv2.VideoCapture(2,cv2.CAP_V4L2)
cap = cv2.VideoCapture("/dev/up_video1",cv2.CAP_V4L2)
# cap = cv2.VideoCapture("/dev/code_video1",cv2.CAP_V4L2)
# cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('Y', 'U', 'Y', 'V'))
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
# cap.set(3, 640)#��
# cap.set(4, 480)#��
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
# cap.set(cv2.CAP_PROP_EXPOSURE, float(0.6)) 
cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
# cap.set(cv2.CAP_PROP_EXPOSURE, float(0.1))
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
# ret = cap.grab()


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


correct_x_hough=36
correct_y_hough=14

def findBlockCenter11(color_cap, color_number):
    flag_color_1 = 0
    red_min = np.array(dim_red_min)
    red_max = np.array(dim_red_max)
    green_min = np.array(dim_green_min1)
    green_max = np.array(dim_green_max1)
    blue_min = np.array(dim_blue_min)
    blue_max = np.array(dim_blue_max)
    red_min1 = np.array(dim_red_min1)
    red_max1 = np.array(dim_red_max1)

    ret = color_cap.grab()
    ret = color_cap.grab()
    ret = color_cap.grab()
    ret, frame = color_cap.read()

    y0, x0 = frame.shape[:2]
    frame_change = cv2.resize(frame, (int(x0), int(y0)))

    src1 = frame_change.copy()
    res1 = src1.copy()
    hsv = cv2.cvtColor(src1, cv2.COLOR_BGR2HSV)

    # ʹ�� Canny ��Ե����ҵ�����
    gray = cv2.cvtColor(src1, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
    cv2.imshow("edges",edges)

    # ������Ĥ�����������µ���������Ϊ��ɫ
    mask = np.ones_like(gray) * 255  # ����ȫ����Ĥ
    if lines is not None:
        longest_line = max(lines, key=lambda line: line[0][2] - line[0][0])  # ������ѡ�����ֱ��
        x1, y1, x2, y2 = longest_line[0]
        if y1 < y2:  # ȷ�� y1 �����ߵ��϶˵�
            cv2.rectangle(mask, (0, y2), (x0, y0), 0, -1)  # ���������������
        else:
            cv2.rectangle(mask, (0, y1), (x0, y0), 0, -1)

    # ����ĤӦ�õ� HSV ͼ��
    hsv = cv2.bitwise_and(hsv, hsv, mask=mask)

    # ������������
    mask12 = cv2.inRange(hsv, red_min, red_max)
    mask11 = cv2.inRange(hsv, red_min1, red_max1)
    mask2 = cv2.inRange(hsv, green_min, green_max)
    mask3 = cv2.inRange(hsv, blue_min, blue_max)
    mask1 = cv2.add(mask12, mask11)

    if color_number == 1:
        mask0 = mask1
    elif color_number == 2:
        mask0 = mask2
    elif color_number == 3:
        mask0 = mask3

    res1 = cv2.bitwise_and(src1, src1, mask=mask0)
    cv2.imshow("res1", res1)

    h, w = res1.shape[:2]
    blured = cv2.blur(res1, (7, 7))
    blured = cv2.blur(res1, (5, 5))
    ret, bright = cv2.threshold(blured, 10, 255, cv2.THRESH_BINARY)

    gray = cv2.cvtColor(bright, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    opened = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    closed1 = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    closed = cv2.morphologyEx(closed1, cv2.MORPH_CLOSE, kernel)

    contours, hierarchy = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    num = 0
    a_sum = 0
    b_sum = 0
    x_min = 4000
    x_max = 0
    y_min = 4000
    y_max = 0
    x_center = 0
    y_center = 0
    c = 0
    detx_p = 0
    dety_p = 0

    for cnt343 in contours:
        (x1, y1, w1, h1) = cv2.boundingRect(cnt343)
        area = cv2.contourArea(cnt343)
        if w1 * h1 > 0.07 * w * h:
            a = x1 + w1 / 2
            b = y1 + h1 / 2
            a_sum += a
            b_sum += b
            num += 1

            cv2.rectangle(src1, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2)
            cv2.putText(src1, 'color', (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            area_text = f"{w1 * h1}"
            cv2.putText(src1, area_text, (x1 + 60, y1 + h1 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            center_text = f"({a}, {b})"
            cv2.putText(src1, center_text, (x1, y1 + h1 + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            color_text = f"{color_number}"
            cv2.putText(src1, color_text, (x1, y1 + h1 + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if num == 1 or c < y1:
                x_center = a
                y_center = b
                c = y1
            flag_color_1 = 1
            detx_p = a - w / 2 - correct_x_hough
            dety_p = h / 2 - correct_y_hough - b
            detx_p = int(detx_p)
            dety_p = int(dety_p)

    cv2.imshow("src1", src1)
    cv2.waitKey(1)
    return x_center / w, y_center / h, frame, flag_color_1, detx_p, dety_p

while True:
    # Time1=time.time()
    success, img = cap.read()
    # print("time:",time.time()-Time1)
    # cv2.imshow("Original",img)



    src1 = img.copy()
    res1 = src1.copy()
    h, w = res1.shape[:2]
    # print("h:",h,"w:,",w)
    # detx,dety,move_flag_color_2=testdef.circlePut1(cap)
    # theta,line_flag,detx,dety,move_flag=testdef.together_line_circle1(cap)
    # a,b,frame,flag_color_1,detx_p,dety_p=findBlockCenter11(cap,2)
    x_,y_,img_,flag9,detx9,dety9,color = testdef.findBlockCenter_gray(cap)

    cv2.waitKey(1)    

cap.release()
cv2.destroyAllWindows()







# import cv2
 
# #ѡ������ͷ�ţ�һ��� 0 ��ʼ
# # cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
# # cap.set(3, 352)#��
# # cap.set(4, 288)#��
# # cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
# # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3.0)
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1.0)
# cap.set(cv2.CAP_PROP_EXPOSURE, 166)
# # cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
# # cap.set(cv2.CAP_PROP_EXPOSURE, float(0.1)) 
# # cap.set(cv2.CAP_PROP_EXPOSURE, 100) 


 
# #�����ò�����Ȼ���ȡ����
# for i in range(47):
#     print("No.={} parameter={}".format(i,cap.get(i)))
 
# while True:
#     ret, img = cap.read()
#     cv2.imshow("input", img)
# # �� ESC ���˳�
#     key = cv2.waitKey(10)
#     if key == 27:
#         break
 
# cv2.destroyAllWindows() 
# cv2.VideoCapture(0).release()





# # import cv2

# # # ��ʼ������ͷ
# # cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
# # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
# # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3.0)  # �ر��Զ��ع�
# # cap.set(cv2.CAP_PROP_EXPOSURE, 166)  # ��ʼ�ع�ֵ

# # # ��������
# # cv2.namedWindow("input")

# # # ����ص����������ڸ����ع�ֵ
# # def update_exposure(value):
# #     cap.set(cv2.CAP_PROP_EXPOSURE, value)

# # # ����������
# # cv2.createTrackbar("Exposure", "input", int(cap.get(cv2.CAP_PROP_EXPOSURE)), 10000, update_exposure)

# # # ��ʾ����ͷͼ��
# # while True:
# #     ret, img = cap.read()
# #     if not ret:
# #         print("�޷���ȡ����ͷͼ��")
# #         break

# #     cv2.imshow("input", img)

# #     # ���� ESC ���˳�
# #     key = cv2.waitKey(10)
# #     if key == 27:
# #         break

# # # �ͷ���Դ���رմ���
# # cap.release()
# # cv2.destroyAllWindows()