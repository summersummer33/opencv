import cv2
import numpy as np
import time
# import uvc
import testdef
import serial


# #��������ͷ��������
# capture_width = 640   #
# capture_height = 480
# framerate = 60			# ֡��

# cap = cv2.VideoCapture(2,cv2.CAP_V4L2)
cap = cv2.VideoCapture("/dev/up_video1",cv2.CAP_V4L2)
# cap = cv2.VideoCapture("/dev/code_video1",cv2.CAP_V4L2)
# cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('Y', 'U', 'Y', 'V'))
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(3, 1280)#��
cap.set(4, 720)#��
# cap.set(3, 640)#��
# cap.set(4, 480)#��
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
# cap.set(cv2.CAP_PROP_EXPOSURE, float(0.6)) 
cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
# cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
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
ser=testdef.serialInit()

i=0
while True:
    # Time1=time.time()
    success, img = cap.read()
    # print("time:",time.time()-Time1)
    cv2.imshow("Original",img)


    src1 = img.copy()
    res1 = src1.copy()
    h, w = res1.shape[:2]
    # print("h:",h,"w:,",w)
    # detx1,dety1,move_flag,stop_flag=testdef.findCountours(cap)
    # detx,dety,move_flag_color_2=testdef.circlePut1(cap)
    # theta,line_flag,detx,dety,move_flag=testdef.together_line_circle1(cap)
    # a,b,frame,flag_color_1,detx_p,dety_p=findBlockCenter11(cap,2)
    # x_,y_,img_,flag9,detx9,dety9,color = testdef.findBlockCenter_gray(cap)
    x_,y_,img_,flag9,detx9,dety9= testdef.findBlockCenter(cap,2)

    # x_,y_,img_,flag_=testdef.findBlockCenter_circle(cap,1)
    # finaltheta,line_flag=testdef.detectLine(cap)
    # x_,y_,img_,move_flag_color_1,detx_p,dety_p = testdef.circlePut_color(cap,2)
    # x_,y_,img_,flag1,detx,dety = testdef.findBlockCenter(cap,3)
    # x_center,y_center,flag_color_1,detx_p,dety_p=testdef.findGoodsCenter(cap,1)

    # finaltheta,line_flag=testdef.detectLine(cap)
    # cap.release()
    cv2.waitKey(1)    

cap.release()
cv2.destroyAllWindows()







# import cv2
# import time
 
# #ѡ������ͷ�ţ�һ��� 0 ��ʼ
# # cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('/dev/up_video1',cv2.CAP_V4L2)
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
# cap.set(3, 1280)#��
# cap.set(4, 720)#��
# # cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
# # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3.0)
# # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1.0)
# # cap.set(cv2.CAP_PROP_EXPOSURE, 166)
# # cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
# # cap.set(cv2.CAP_PROP_EXPOSURE, float(0.1)) 
# # cap.set(cv2.CAP_PROP_EXPOSURE, 10000 * 2**(-12))
# # cap.set(cv2.CAP_PROP_HUE, 0) 


 
# #�����ò�����Ȼ���ȡ����
# for i in range(47):
#     print("No.={} parameter={}".format(i,cap.get(i)))
 
# while True:
#     # time1=time.time()
#     ret, img = cap.read()
#     cv2.imshow("input", img)
#     # print(time.time()-time1)

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