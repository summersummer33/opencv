import cv2
import numpy as np
import math
import time
import serial 
import testdef
import threading





# #multi_threading
# global cap
# class VideoCaptureThread:
#     def __init__(self, index=0):
#         self.cap = cv2.VideoCapture("/dev/up_video",cv2.CAP_V4L2)
#         self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
#         self.cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
#         # self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
#         self.frame = None
#         self.running = True
#         self.lock = threading.Lock()
#         self.thread = threading.Thread(target=self.update)
#         self.thread.start()

#     def update(self):
#         while self.running:
#             ret, frame = self.cap.read()
#             if ret:
#                 with self.lock:  # ȷ���̰߳�ȫ
#                     self.frame = frame

#     def read(self):
#         with self.lock:  # ȷ���̰߳�ȫ
#             return self.frame

#     def stop(self):
#         self.running = False
#         self.thread.join()
#         self.cap.release()


# # ʹ��ʾ��
# cap = VideoCaptureThread()

###################################

frameWidth = 640
frameHeight = 480
global cap
# cap = cv2.VideoCapture("/dev/up_video",cv2.CAP_V4L2)
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
# cap.set(3, frameWidth)
# cap.set(4, frameHeight)
# cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
# cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)




#ttyAMA0

# code_cap = cv2.VideoCapture("/dev/code_video",cv2.CAP_V4L2)  
code_cap = cv2.VideoCapture(2,cv2.CAP_V4L2) 
code_cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
code_cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

ser=testdef.serialInit()

dim_red_min =   [  0, 133,68]
dim_red_max =   [ 11,255, 255]
dim_green_min = [44,51,0]# 60 60
dim_green_max = [67,255,255]
# dim_blue_min =  [66,90,74] 
# dim_blue_max =  [163,203,255]
dim_blue_min =  [101,56,0]
dim_blue_max =  [130,255,255]
global data1
global data2
global color_cap
global color_number
get_order=[]
put_order=[]
line_flag=0
move_flag=0
move_flag_color=0
move_flag_color_1=0
move_flag_color_2=0
circle_time = 1 
circle_order=[]
plate_time=1  #zhuanpanjishu
plate_order=[]
# recv = b'BB'
recv=''
line_cishu =1
get_order=[2,3,1]
while True:
    # get_order=[2,3,1]
    # # get_order=[3,3,3]
    # put_order=[1,2,3]

    recv_mess = testdef.receiveMessage(ser)
    if recv_mess != None:
        print("recv_mess:",recv_mess)
    if recv_mess != None:
        if recv_mess == b'AA' or recv_mess==b'BB' or recv_mess==b'CC' or recv_mess==b'DD' or recv_mess==b'EE' or recv_mess==b'FF' or recv_mess==b'GG' or recv_mess==b'st':
            recv=recv_mess
    # print("first  recv:",recv)
    print(recv)
    # success, img = cap.read()


    if recv==b'AA':     #shibie code
        # code_cap = cv2.VideoCapture("/dev/code_video",cv2.CAP_V4L2)  
        # code_cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        # code_cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)


        # su,fr=cap.read()
        # cv2.imshow("up",fr)p

        while True:
            data,code_flag = testdef.code(code_cap)
            if(len(data) == 7 and code_flag == 1):
                break
        # Stm_serial.write(('c'+data).encode())
        print(data)
        data1 = data[0:3]
        data2 = data[4:7]
        print("data1",data1)
        print("data2",data2)
        get_order=testdef.sort(data1)
        put_order=testdef.sort(data2)
        order=get_order+put_order
        # print("get",get_order)
        # print("put",put_order)
        # testdef.sendMessage3(ser,get_order)   #Ҫ����stm32
        # testdef.sendMessage3(ser,put_order)
        testdef.sendMessage3(ser,order)
        time.sleep(0.01)
        testdef.sendMessage3(ser,order)
        time.sleep(0.01)
        testdef.sendMessage3(ser,order)
        code_cap.release()
        cv2.destroyAllWindows()
        # time.sleep(3)
        print("close")
        # cap = cv2.VideoCapture("/dev/up_video",cv2.CAP_V4L2)
        cap = cv2.VideoCapture("/dev/up_video",cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        cap.set(3, frameWidth)
        cap.set(4, frameHeight)
        cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
        

        recv=b'st'

    #! 这是红色注释  
    #? 这是蓝色注释
    #TODO 这是橙色注释
    

    #Բ�̴�ץ���  
    elif recv==b'BB':      #shibie zhuanpan    
        i=0
        while not cap.isOpened():
            print("Not open colorcap")
        if plate_time == 1:
            plate_order=get_order
        elif plate_time == 2:
            plate_order=put_order
        # plate_order=get_order
        print("pkate_order:",plate_order)
        stop_flag=0
        # i=0
        while i<3:
        # for i in range(3):
            # print("iii:",i)
            # flagno = testdef.detectPlate(cap, 1)
            while not stop_flag:
                print("i:",i)
                flag2 = testdef.detectPlate(cap,plate_order[i])
                x_,y_,img_,flag1,detx,dety = testdef.findBlockCenter(cap,plate_order[i])
                if  (flag2 == 1 and flag1 == 1):
                    stop_flag = plate_order[i]
                    print("stop_flag",stop_flag)
                    # if i==0:#��һ��ʶ��ʱ����Բ������ֵ������е��
                    testdef.sendMessage2(ser,detx,dety)#?????��ô����
                    time.sleep(0.01)
                    if stop_flag == 1:
                        testdef.sendMessage(ser,7)
                    elif stop_flag == 2:
                        testdef.sendMessage(ser,8)
                    elif stop_flag == 3:
                        testdef.sendMessage(ser,9)
                    # testdef.sendMessage(ser,stop_flag)
            Time = time.time()
            stop_flag=0
            flag_check=0
            if i == 0:
                Time1=time.time()-Time
                print("Time1:",Time1)
                time.sleep(0.7)
                print("start checkkkkkkkkkkkkkkkkkkk")
                flag_check=testdef.detectPlate_check(cap,plate_order[i])
                Time2=time.time()-Time
                print("Time2:",Time2)
                print("flag_chexk:",flag_check)
                if flag_check :
                    print("next colorrrrrrrrrrrrrrrrrrrr")
                    i=i+1
                else:
                    testdef.sendMessage(ser,3)
            else :
                time.sleep(3)
                i=i+1
            # time.sleep(3)
            # i=i+1
        plate_time += 1
        cv2.destroyAllWindows()
        recv=b'st'

        
   
    # #Բ������λ���գ�
    # elif recv==b'CC':       #shibie yuanhuan
    #     print("cccccccccccc")
    #     print("line_flag===",line_flag,"move_flag===",move_flag)
    #     while not cap.isOpened():
    #         print("Not open colorcap")
    #     # if(line_cishu == 2 or line_cishu ==4):
    #     while not line_flag:
    #         recvv=testdef.receiveMessage(ser)
    #         if recvv==b'next_line':
    #             print("recvvvvvvvvvv:",recvv)
    #             line_flag=0
    #             break
    #         theta,line_flag=testdef.detectLine(cap)
    #         if line_flag ==0:
    #             testdef.sendMessage4(ser,theta)
    #             print("main li de theta:",theta)
    #         elif line_flag==1:
    #             print("line_flag:",line_flag)
    #             testdef.sendMessage(ser,39)
    #             time.sleep(0.01)
    #             testdef.sendMessage(ser,40)
    #             break
    #     # # cv2.destroyAllWindows()
    #     while not move_flag:
    #         recvv1=testdef.receiveMessage(ser)
    #         print(recvv1)
    #         if recvv1==b'next':
    #             # recv=b'st'
    #             line_flag=0
    #             print("recv=",recvv1,"line_flag=",line_flag)
    #             print("outttttttttttttttttttttttttttttttttttt")
    #             break
    #         for i in range(5):
    #             detxq,detyq,move_dirq,move_flagq=testdef.findCountours(cap)
    #         detx,dety,move_dir,move_flag=testdef.findCountours(cap)
    #         if move_flag==0:
    #             testdef.sendMessage2(ser,detx,dety)
    #         elif move_flag==1:                          
    #             print("move_flag:",move_flag)
    #             # testdef.sendMessage(ser,23)
    #             # time.sleep(0.1)
    #             # testdef.sendMessage(ser,23)                
    #             # time.sleep(0.1)
    #             testdef.sendMessage(ser,23)
    #             time.sleep(0.01)
    #             testdef.sendMessage(ser,24)
            
    #             break
    #     move_flag=0
    #     line_flag=0


    #     circle_order=get_order
    #     for i in range(3):
    #         print("iiiiiiiiiiiiii:",i)
    #         recv_first=None
    #         # for j in range(3):
    #         #     x1_,y1_,img1_,flag11,detx1_p,dety1_p = testdef.circlePut_color(cap,circle_order[i])
    #         while True:
    #             recv_first=testdef.receiveMessage(ser)
    #             print("recv_first",recv_first)
    #             if recv_first==b'near ground':
    #                 break
    #         recv1=None
    #         while True:
    #             print("cccccccccccc")
    #             recv1=testdef.receiveMessage(ser)
    #             if recv1==b'next_1':
    #                 print("recvvvvvvvvvv111:",recv1)
    #                 break
    #             # print("iiiiiiiiiiinnnnnnnnnnnnnnnn")
    #             for j in range(3):
    #                 ret=cap.grab()
    #             # print("beforebeforebeforebefore")
    #             x_,y_,img_,flag1,detx_p,dety_p = testdef.circlePut_color(cap,circle_order[i])
    #             # print("afterafterafterafter")
    #             if abs(detx_p)<12 and abs(dety_p)<12:
    #                 move_flag_color=1
    #                 break
    #             else:
    #                 testdef.sendMessage2(ser,detx_p,dety_p)
    #         move_flag_color=0   
    #         while not move_flag:
    #             print("xxxxxxxx")
    #             if recv1==b'next_1':
    #                 print("recvvvvvvvvvv111:",recv1)
    #                 recv1=None
    #                 break
    #             recv2=testdef.receiveMessage(ser)
    #             if recv2==b'next_1':
    #                 print("recvvvvvvvvvv222:",recv2)
    #                 break
    #             for j in range(3):
    #                 ret=cap.grab()
    #             detx,dety,move_flag=testdef.circlePut1(cap)
    #             if move_flag==0:
    #                 testdef.sendMessage2(ser,detx,dety)
    #             elif move_flag==1:                          
    #                 print("move_flag:",move_flag)
    #                 testdef.sendMessage(ser,57)
    #                 time.sleep(0.01)
    #                 break
    #         move_flag=0
    #         i = i+1
    #     circle_time +=1

        
    #     recv=b'st'
    #     line_cishu+=1
    #     # cv2.destroyAllWindows()
        

    # elif recv==b'CC':       #����ݮ������㳬ʱ
    #     print("cccccccccccc")
    #     print("line_flag===",line_flag,"move_flag===",move_flag)
    #     while not cap.isOpened():
    #         print("Not open colorcap")
    #     # if(line_cishu == 2 or line_cishu ==4):
    #     #ֱ�ߵ���
    #     Time1=time.time()
    #     time_line=5
    #     while (not line_flag and (time.time()-Time1)<  time_line):
    #         theta,line_flag=testdef.detectLine(cap)
    #         if line_flag ==0:
    #             testdef.sendMessage4(ser,theta)
    #             # print("main li de theta:",theta)
    #         # elif line_flag==1:
    #         #     # print("line_flag:",line_flag)
    #         #     print("line okokokokokokokokok")
    #         #     testdef.sendMessage(ser,39)
    #         #     time.sleep(0.01)
    #         #     testdef.sendMessage(ser,40)
    #         #     break
    #     # # cv2.destroyAllWindows()
    #     print("line okokokokokokokokok  line_flag:",line_flag)
    #     testdef.sendMessage(ser,39)
    #     time.sleep(0.01)
    #     testdef.sendMessage(ser,40)
    #     #�����̴ֵ�
    #     Time2=time.time()
    #     time_cu=5
    #     while (not move_flag and (time.time()-Time2)<time_cu):
    #         for i in range(5):
    #             detxq,detyq,move_dirq,move_flagq=testdef.findCountours(cap)
    #         detx,dety,move_dir,move_flag=testdef.findCountours(cap)
    #         if move_flag==0:
    #             testdef.sendMessage2(ser,detx,dety)
    #         # elif move_flag==1:                          
    #         #     # print("move_flag:",move_flag)
    #         #     print("cutiao okokokokokokokokok")
    #         #     testdef.sendMessage(ser,23)
    #         #     time.sleep(0.01)
    #         #     testdef.sendMessage(ser,24)
    #         #     break
    #     print("cutiao okokokokokokokokok   move_flag:",move_flag)
    #     testdef.sendMessage(ser,23)
    #     time.sleep(0.01)
    #     testdef.sendMessage(ser,24)
    #     move_flag=0
    #     line_flag=0

    #     #����е��ϸ��
    #     circle_order=get_order
    #     for i in range(3):
    #         print("iiiiiiiiiiiiii:",i,"color:",circle_order[i])
    #         recv_first=None
    #         # for j in range(3):
    #         #     x1_,y1_,img1_,flag11,detx1_p,dety1_p = testdef.circlePut_color(cap,circle_order[i])
    #         while True:
    #             recv_first=testdef.receiveMessage(ser)
    #             print("recv_first",recv_first)
    #             if recv_first==b'near ground':
    #                 break
    #         Time3=time.time()
    #         time_xi=3
    #         #��һ����ϸ��
    #         while (not move_flag_color_1 and (time.time()-Time3)<time_xi):
    #             print("cccccccccccc")
    #             # print("iiiiiiiiiiinnnnnnnnnnnnnnnn")
    #             for j in range(3):
    #                 ret=cap.grab()
    #             x_,y_,img_,flag1,detx_p,dety_p = testdef.circlePut_color(cap,circle_order[i])
    #             if abs(detx_p)<12 and abs(dety_p)<12:
    #                 print("xitiao11 okokokokokokokokok")
    #                 move_flag_color_1=1
    #                 break
    #             else:
    #                 testdef.sendMessage2(ser,detx_p,dety_p)
    #         move_flag_color_1=0   
    #         #�ڶ�����ϸ��
    #         while (not move_flag_color_2 and (time.time()-Time3)<time_xi):
    #             print("xxxxxxxx")
    #             for j in range(3):
    #                 ret=cap.grab()
    #             detx,dety,move_flag_color_2=testdef.circlePut1(cap)
    #             if move_flag_color_2==0:
    #                 testdef.sendMessage2(ser,detx,dety)
    #             # elif move_flag_color_2==1:                          
    #             #     # print("move_flag:",move_flag_color_2)
    #             #     print("xitiao22 okokokokokokokokok")
    #             #     testdef.sendMessage(ser,57)
    #             #     time.sleep(0.01)
    #             #     break
    #         print("xitiao22 okokokokokokokokok move_flag_color_2:",move_flag_color_2)
    #         testdef.sendMessage(ser,57)
    #         time.sleep(0.01)
    #         move_flag_color_2=0
    #         i = i+1
    #     circle_time +=1
    #     recv=b'st'
    #     line_cishu+=1


    elif recv==b'CC':       #ֱ�ߺͶ����̵Ĵֵ�����һ��
        print("cccccccccccc")
        print("line_flag===",line_flag,"move_flag===",move_flag)
        while not cap.isOpened():
            print("Not open colorcap")
        # if(line_cishu == 2 or line_cishu ==4):
        Time1=time.time()   
        time_together=5
        # for i in range(5):
        #     ret=cap.grab()
        #     ret=cap.grab()
        #     ret=cap.grab()
        #     ret=cap.grab()
        while ((time.time()-Time1)<time_together) and ((not line_flag) or (not move_flag)) :
            theta,line_flag,detx,dety,move_flag=testdef.together_line_circle1(cap)
            if line_flag==0 or move_flag==0:
                if line_flag ==1:
                    theta=0
                if move_flag ==1:
                    detx=0
                    dety=0
                testdef.sendMessage5(ser,theta,detx,dety)
                # testdef.sendMessage5(ser,theta,0,0)
        print("together okokokokokokokokok line_flag:",line_flag,"move_flag:",move_flag)
        testdef.sendMessage(ser,68)
        time.sleep(0.01)
        move_flag=0
        line_flag=0

        # #����е��ϸ��
        # if circle_time==1 or circle_time==2:
        #     circle_order=get_order
        # elif circle_time==3:
        #     circle_order=put_order
        if circle_time<4:
            print("circle_time:",circle_time)
            if circle_time==1 or circle_time==2:
                circle_order=get_order
            elif circle_time==3:
                circle_order=put_order
            for i in range(3):
                print("iiiiiiiiiiiiii:",i,"color:",circle_order[i])
                recv_first=None
                # for j in range(3):
                #     x1_,y1_,img1_,flag11,detx1_p,dety1_p = testdef.circlePut_color(cap,circle_order[i])
                while True:
                    recv_first=testdef.receiveMessage(ser)
                    print("recv_first",recv_first)
                    if recv_first==b'near ground':
                        break
                Time3=time.time()
                time_xi=5
                #��һ����ϸ��
                while (not move_flag_color_1 and (time.time()-Time3)<time_xi):
                # while (not move_flag_color_1):
                    timee=time.time()
                    print("cccccccccccc")
                    # print("iiiiiiiiiiinnnnnnnnnnnnnnnn")
                    # for j in range(3):
                    #     ret=cap.grab()
                    x_,y_,img_,flag1,detx_p,dety_p = testdef.circlePut_color(cap,circle_order[i])
                    if abs(detx_p)<12 and abs(dety_p)<12:
                        print("xitiao11 okokokokokokokokok")
                        move_flag_color_1=1
                        break
                    else:
                        testdef.sendMessage2(ser,detx_p,dety_p)
                        print("cutiao time:",time.time()-timee)
                        # cutiaojieshou=testdef.receiveMessage(ser)
                        # print("cutiaojieshou:",cutiaojieshou)
                move_flag_color_1=0   
                #�ڶ�����ϸ��
                while (not move_flag_color_2 and (time.time()-Time3)<time_xi):
                # while (not move_flag_color_2 ):
                    print("xxxxxxxx")
                    timeee=time.time()
                    # for j in range(3):
                    #     ret=cap.grab()
                    # detxx=0
                    # detyy=0
                    # flagg=0
                    # for k in range(5):
                    #     detx,dety,move_flag_color_2=testdef.circlePut1(cap)
                    #     detxx+=detx
                    #     detyy+=dety
                    #     flagg+=move_flag_color_2
                    # if flagg==0:
                    #     testdef.sendMessage2(ser,detxx,detyy)
                    detx,dety,move_flag_color_2=testdef.circlePut1(cap)
                    if move_flag_color_2==0:
                        testdef.sendMessage2(ser,detx,dety)
                        print("xitiao time:",time.time()-timeee)
                print("xitiao22 okokokokokokokokok  move_flag_color_2:",move_flag_color_2)
                if circle_order[i] == 1:
                    testdef.sendMessage(ser,57)
                elif circle_order[i] == 2:
                    testdef.sendMessage(ser,64)
                elif circle_order[i] == 3:
                    testdef.sendMessage(ser,65)
                time.sleep(0.01)
                move_flag_color_2=0
                i = i+1
            circle_time +=1


        # cv2.destroyAllWindows()
        recv=b'st'




    elif recv==b'DD':      #shibie zhuanpan2
        while not cap.isOpened():
            print("Not open colorcap")
        stop_flag=0
        for i in range(3):
            # flagno = testdef.detectPlate(cap, 1)
            while not stop_flag:
                flag2 = testdef.detectPlate(cap,put_order[i])
                x_,y_,img_,flag1 = testdef.findBlockCenter(cap,put_order[i])
                if  (flag2 == 1 and flag1 == 1):
                    stop_flag = put_order[i]
                    print("stop_flag",stop_flag)
                    if stop_flag == 1:
                        testdef.sendMessage(ser,7)
                    elif stop_flag == 2:
                        testdef.sendMessage(ser,8)
                    elif stop_flag == 3:
                        testdef.sendMessage(ser,9)
            stop_flag=0
            time.sleep(3)
            i=i+1
        # recv=
        cv2.destroyAllWindows()
        recv=b'st'

    
    elif recv==b'EE':
        while not cap.isOpened():
            print("Not open colorcap")
        Time_l=time.time()
        time_l=2
        while (not line_flag and (time.time()-Time_l)<time_l):
            for i in range(4):
                # theta1,line_flag1=testdef.detectLine(cap)
                ret=cap.grab()
            theta,line_flag=testdef.detectLine_gray(cap)
            if line_flag ==0:
                testdef.sendMessage4(ser,theta)
                print("main li de theta:",theta)
            # elif line_flag==1:
        print("line_flag:",line_flag)
        testdef.sendMessage(ser,39)
        time.sleep(0.01)
        testdef.sendMessage(ser,40)
                # break
        line_flag=0

        # while not cap.isOpened():
        #     print("Not open colorcap")
        # # if(line_cishu == 2 or line_cishu ==4):
        # Time1=time.time()   
        # time_together=10
        # for i in range(5):
        #     ret=cap.grab()
        #     ret=cap.grab()
        #     ret=cap.grab()
        #     ret=cap.grab()
        # while ((time.time()-Time1)<time_together) and ((not line_flag) or (not move_flag)) :
        #     theta,line_flag,detx,dety,move_flag=testdef.together_line_circle1(cap)
        #     if line_flag==0 or move_flag==0:
        #         if line_flag ==1:
        #             theta=0
        #         if move_flag ==1:
        #             detx=0
        #             dety=0
        #         # testdef.sendMessage5(ser,theta,detx,dety)
        #         print("theta:",theta)
        #         testdef.sendMessage4(ser,theta)
        # print("together okokokokokokokokok line_flag:",line_flag,"move_flag:",move_flag)
        # # testdef.sendMessage(ser,68)
        # testdef.sendMessage(ser,39)
        # time.sleep(0.01)
        # testdef.sendMessage(ser,40)    
        # # time.sleep(0.01)
        # move_flag=0
        # line_flag=0

        recv=b'st'

    #only gray
    elif recv==b'FF':
        while not move_flag:
            recvv=testdef.receiveMessage(ser)
            # print(recvv)
            if recvv!=None:
                recv=b'st'
                line_flag=0
                print("recv=",recv,"line_flag=",line_flag)
                print("outttttttttttttttttttttttttttttttttttt")
                break
            recv0=testdef.receiveMessage(ser)
            for i in range(3):
                # detxq,detyq,move_flagq=testdef.circlePut1(cap)
                ret=cap.grab()
            detx,dety,move_flag=testdef.circlePut1(cap)
            if recv0 != None:
                    print("00000000000recv0000:",recv0)
            if move_flag==0:
                testdef.sendMessage2(ser,detx,dety)
            elif move_flag==1:                          
                print("move_flag:",move_flag)
                testdef.sendMessage(ser,57)
                time.sleep(0.01)
            
                break
        move_flag=0
        line_flag=0
        recv=b'st'
        line_cishu+=1



    elif recv==b'GG':
        # while not move_flag_color:
        # if circle_time == 1 or circle_time == 2:
        #     circle_order=get_order
        # elif circle_time == 3 or circle_time == 4:
        #     circle_order=put_order
        #��ֱ�ߣ��������ж��Ƿ�����ɫ���ֵ�
        circle_order=get_order
        # for i in range(3):
        #     print("iiiiiiiiiiiiii:",i)
        #     recv_first=None
        #     for j in range(3):
        #         x1_,y1_,img1_,flag11,detx1_p,dety1_p = testdef.circlePut_color(cap,circle_order[i])
        #     while True:
        #         recv_first=testdef.receiveMessage(ser)
        #         print("recv_first",recv_first)
        #         if recv_first==b'near ground':
        #             break
        #     recv1=None
        #     while True:
        #         print("cccccccccccc")
        #         recv1=testdef.receiveMessage(ser)
        #         if recv1==b'next':
        #             print("recvvvvvvvvvv111:",recv1)
        #             break
        #         # print("iiiiiiiiiiinnnnnnnnnnnnnnnn")
        #         for j in range(3):
        #             ret=cap.grab()
        #         # print("beforebeforebeforebefore")
        #         x_,y_,img_,flag1,detx_p,dety_p = testdef.circlePut_color(cap,circle_order[i])
        #         # print("afterafterafterafter")
        #         if abs(detx_p)<12 and abs(dety_p)<12:
        #             move_flag_color=1
        #             break
        #         else:
        #             testdef.sendMessage2(ser,detx_p,dety_p)
        #     move_flag_color=0   
        #     while not move_flag:
        #         print("xxxxxxxx")
        #         if recv1==b'next':
        #             print("recvvvvvvvvvv111:",recv1)
        #             recv1=None
        #             break
        #         recv2=testdef.receiveMessage(ser)
        #         if recv2==b'next':
        #             print("recvvvvvvvvvv222:",recv2)
        #             break
        #         for j in range(3):
        #             ret=cap.grab()
        #         detx,dety,move_flag=testdef.circlePut1(cap)
        #         if move_flag==0:
        #             testdef.sendMessage2(ser,detx,dety)
        #         elif move_flag==1:                          
        #             print("move_flag:",move_flag)
        #             testdef.sendMessage(ser,57)
        #             time.sleep(0.01)
        #             break
        #     move_flag=0
        #     i = i+1
        # circle_time +=1
        # # line_flag=0


        for i in range(3):
                print("iiiiiiiiiiiiii:",i,"color:",circle_order[i])
                recv_first=None
                # for j in range(3):
                #     x1_,y1_,img1_,flag11,detx1_p,dety1_p = testdef.circlePut_color(cap,circle_order[i])
                while True:
                    recv_first=testdef.receiveMessage(ser)
                    print("recv_first",recv_first)
                    if recv_first==b'near ground':
                        break
                Time3=time.time()
                time_xi=5
                #��һ����ϸ��
                while (not move_flag_color_1 and (time.time()-Time3)<time_xi):
                # while (not move_flag_color_1):
                    print("cccccccccccc")
                    # print("iiiiiiiiiiinnnnnnnnnnnnnnnn")
                    for j in range(3):
                        ret=cap.grab()
                    x_,y_,img_,flag1,detx_p,dety_p = testdef.circlePut_color(cap,circle_order[i])
                    if abs(detx_p)<10 and abs(dety_p)<10:
                        print("xitiao11 okokokokokokokokok")
                        move_flag_color_1=1
                        break
                    else:
                        testdef.sendMessage2(ser,detx_p,dety_p)
                        # cutiaojieshou=testdef.receiveMessage(ser)
                        # print("cutiaojieshou:",cutiaojieshou)
                move_flag_color_1=0   
                #�ڶ�����ϸ��
                while (not move_flag_color_2 and (time.time()-Time3)<time_xi):
                # while (not move_flag_color_2 ):
                    print("xxxxxxxx")
                    for j in range(3):
                        ret=cap.grab()
                    detx,dety,move_flag_color_2=testdef.circlePut1(cap)
                    if move_flag_color_2==0:
                        testdef.sendMessage2(ser,detx,dety)
                print("xitiao22 okokokokokokokokok  move_flag_color_2:",move_flag_color_2)
                if circle_order[i] == 1:
                    testdef.sendMessage(ser,57)
                elif circle_order[i] == 2:
                    testdef.sendMessage(ser,64)
                elif circle_order[i] == 3:
                    testdef.sendMessage(ser,65)
                time.sleep(0.01)
                move_flag_color_2=0
                i = i+1
        recv=b'st'

        
        

    elif recv=='03':       #ceshi shiyong
        theta,line_flag=testdef.detectLine(cap)
        # testdef.sendMessage(ser,theta)
        # print(theta)

        # data=testdef.receiveMessage(ser)
        # print(data)

    elif recv=='04':
        recvvv=testdef.receiveMessage(ser)
        
        if recvvv!=None:
            print("recvvv:",recvvv)
        if recvvv==b'AA':
            print("function1")

    elif recv=='05':   #test putcircle
        while not cap.isOpened():
            print("Not open colorcap")
        while not line_flag:
            theta,line_flag=testdef.detectLine(cap)
            testdef.sendMessage4(ser,theta)
            print(theta)
            if line_flag==1:
                print("line_flag:",line_flag)
                testdef.sendMessage(ser,39)
                time.sleep(0.01)
                testdef.sendMessage(ser,40)
                break
        cv2.destroyAllWindows()
        while not move_flag:
            detx1,dety1,move_flag=testdef.circlePut_color(cap)
            testdef.sendMessage2(ser,detx1,dety1)
            if move_flag==1:                          
                print("move_flag:",move_flag)
                testdef.sendMessage(ser,23)
                time.sleep(0.01)
                testdef.sendMessage(ser,24)
                move_flag=0
                break

        circle_order=put_order
        for i in range(3):
            print("iiiiiiiiiiiiii:",i,"color:",circle_order[i])
            recv_first=None
            # for j in range(3):
            #     x1_,y1_,img1_,flag11,detx1_p,dety1_p = testdef.circlePut_color(cap,circle_order[i])
            while True:
                recv_first=testdef.receiveMessage(ser)
                print("recv_first",recv_first)
                if recv_first==b'near ground':
                    break
            Time3=time.time()
            time_xi=1.5
            #��һ����ϸ��
            while (not move_flag_color_1 and (time.time()-Time3)<time_xi):
            # while (not move_flag_color_1):
                print("cccccccccccc")
                # print("iiiiiiiiiiinnnnnnnnnnnnnnnn")
                for j in range(3):
                    ret=cap.grab()
                x_,y_,img_,flag1,detx_p,dety_p = testdef.circlePut_color(cap,circle_order[i])
                if abs(detx_p)<12 and abs(dety_p)<12:
                    print("xitiao11 okokokokokokokokok")
                    move_flag_color_1=1
                    break
                else:
                    testdef.sendMessage2(ser,detx_p,dety_p)
            move_flag_color_1=0   
            #�ڶ�����ϸ�
            # while (not move_flag_color_2 and (time.time()-Time3)<time_xi):
            # # while (not move_flag_color_2 ):
            #     print("xxxxxxxx")
            #     for j in range(3):
            #         ret=cap.grab()
            #     detx,dety,move_flag_color_2=testdef.circlePut1(cap)
            #     if move_flag_color_2==0:
            #         testdef.sendMessage2(ser,detx,dety)
            # print("xitiao22 okokokokokokokokok  move_flag_color_2:",move_flag_color_2)
            if circle_order[i] == 1:
                testdef.sendMessage(ser,57)
            elif circle_order[i] == 2:
                testdef.sendMessage(ser,64)
            elif circle_order[i] == 3:
                testdef.sendMessage(ser,65)
            time.sleep(0.01)
            move_flag_color_2=0
            i = i+1

    elif recv==b'st':
        pass

    elif recv==b'end':
        break


    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# code_cap.release()
cap.release()
cv2.destroyAllWindows()

