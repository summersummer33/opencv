import cv2
import numpy as np
import math
import time
import serial 
import testdef
import threading




##################################

frameWidth = 1280
frameHeight = 720
global cap
#初始化上部摄像头（调试时使用 正式运行时注释掉
cap = cv2.VideoCapture("/dev/up_video1",cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(3, frameWidth)
cap.set(4, frameHeight)
cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)

#初始化侧边二维码摄像头
# code_cap=None
code_cap = cv2.VideoCapture("/dev/code_video1",cv2.CAP_V4L2)  
code_cap.set(cv2.CAP_PROP_FRAME_WIDTH,frameWidth)
code_cap.set(cv2.CAP_PROP_FRAME_HEIGHT,frameHeight)
code_cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
code_cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
if code_cap.isOpened():
    print("start      successsssssssss")
else:
    print("start      faillllllllll")

#初始化串口
ser=testdef.serialInit()

# #颜色阈值hsv
# dim_red_min =   [  0, 133,68]
# dim_red_max =   [ 11,255, 255]
# dim_green_min = [44,51,0]# 60 60
# dim_green_max = [67,255,255]
# # dim_blue_min =  [66,90,74] 
# # dim_blue_max =  [163,203,255]
# dim_blue_min =  [101,56,0]
# dim_blue_max =  [130,255,255]
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
# recv = b'AA'
recv=''
line_cishu =1
get_order=[2,1,3]
put_order=[2,1,3]
get_order_blank=[]




while True:
    #### 接收串口数据
    recv_mess = testdef.receiveMessage(ser)
    if recv_mess != None:
        print("recv_mess:",recv_mess)
    if recv_mess != None:
        #### 根据接收到的指令更新recv
        # if (recv_mess == b'AA' or recv_mess==b'BB' or recv_mess==b'CC' or recv_mess==b'DD' or recv_mess==b'EE' 
        #     or recv_mess==b'FF' or recv_mess==b'GG' or recv_mess==b'HH' or recv_mess==b'LL' or recv_mess==b'st'):
        if recv_mess in [b'AA', b'BB', b'CC', b'DD', b'EE', b'FF', b'GG', b'HH', b'II', b'JJ', b'KK', b'LL', b'MM', b'NN', b'OO', b'PP', b'st', b'end']:
            recv=recv_mess
    # print("first  recv:",recv)
    print(recv)


    #############################################################################################
    ########################初赛正常流程使用代码（轻易不要改动！！！）###############################
    #############################################################################################

####识别二维码、条形码
    if recv==b'AA': 
        time_c=time.time()
        time_code=10
        code_end=0
        if code_cap.isOpened():
            print("11      successsssssssss")
        else:
            print("11     faillllllllll")
        # while True:
        while (time.time()-time_c)<time_code and (not code_end):
            data,code_flag = testdef.code(code_cap)  #处理二维码图像
            if(len(data) == 7 and code_flag == 1):
                code_end=1
                break
        print(data)
        data1 = data[0:3]
        data2 = data[4:7]
        # print("data1",data1)
        # print("data2",data2)
        if code_end==1:
            get_order=testdef.sort(data1)
            put_order=testdef.sort(data2)
        order=get_order+put_order
        ####二维码信息发送给stm32
        testdef.sendMessage3(ser,order)
        time.sleep(0.01)
        testdef.sendMessage3(ser,order)
        time.sleep(0.01)
        testdef.sendMessage3(ser,order)
        code_cap.release()
        # code_cap=None
        cv2.destroyAllWindows()
        # time.sleep(3)
        ####初始化上部摄像头
        # cap = cv2.VideoCapture("/dev/up_video1",cv2.CAP_V4L2)
        # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        # cap.set(3, frameWidth)
        # cap.set(4, frameHeight)
        # cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
        # cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
        # # cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
        #结束功能后进入空循环
        recv=b'st'


####识别转盘 夹取物料（正常流程
    elif recv==b'BB':      
        while not cap.isOpened():
            print("Not open colorcap")
        ####根据运行轮数使用不同顺序
        if plate_time == 1:
            plate_order=get_order
        elif plate_time == 2:
            plate_order=put_order
        print("plate_order:",plate_order)
        stop_flag=0   #初始化转盘是否停止标志位
        i=0   #运行轮数
        while i<3:
        ####依据颜色顺序循环处理3个物料
            # print("iii:",i)
            # flagno = testdef.detectPlate(cap, 1)
            while not stop_flag:
                print("i:",i)
                flag2 = testdef.detectPlate(cap,plate_order[i])
                x_,y_,img_,flag1,detx,dety = testdef.findBlockCenter(cap,plate_order[i])
                ####当所看对应颜色物料静止时
                if  (flag2 == 1 and flag1 == 1):
                    stop_flag = plate_order[i]  #令标志位为颜色序号
                    print("stop_flag",stop_flag)
                    testdef.sendMessage2(ser,detx,dety)  #给机械臂发送大致调整参数，机械臂只动一下
                    time.sleep(0.01)
                    if stop_flag == 1:  #发送到位信息，不同颜色发送不同值
                        testdef.sendMessage(ser,7)
                    elif stop_flag == 2:
                        testdef.sendMessage(ser,8)
                    elif stop_flag == 3:
                        testdef.sendMessage(ser,9)
                    # testdef.sendMessage(ser,stop_flag)
            # Time = time.time()
            stop_flag=0    #重置停止标志位，给下一轮使用
            flag_check=0    #初始化、重置检查物料是否夹到标志位
            ####在第一次夹取时进行二次检查 确保夹到了第一个物料
            if i == 0:
                # Time1=time.time()-Time
                # print("Time1:",Time1)
                time.sleep(0.5)
                print("start checkkkkkkkkkkkkkkkkkkk")
                flag_check=testdef.detectPlate_check(cap,plate_order[i])
                # Time2=time.time()-Time
                # print("Time2:",Time2)
                print("flag_chexk:",flag_check)
                if flag_check :  #如果夹到了继续下一个颜色
                    print("next colorrrrrrrrrrrrrrrrrrrr")
                    i=i+1
                else:  #没夹到仍等待第一个,机械臂不回头放物料，直接下降
                    testdef.sendMessage(ser,3)
            else :
                time.sleep(3)
                i=i+1
            # time.sleep(3)
            # i=i+1
        plate_time += 1  #轮数+1
        cv2.destroyAllWindows()
        recv=b'st'


####识别圆环 放置物料
    elif recv==b'CC':       
        print("cccccccccccc")
        line_flag=0   #粗调时的直线圆环标志位置0
        move_flag=0
        while not cap.isOpened():
            print("Not open colorcap")
        for i in range(2):
            q=cap.grab()
        ####粗调 圆环粗定位和直线一起调整
        ####粗调开始计时
        Time1=time.time()   
        time_together=7   #粗调超时
        ####发送偏差值信息，调整车身位置直到超时或者直线圆环均到位
        while ((time.time()-Time1)<time_together) and ((not line_flag) or (not move_flag)) :
            theta,line_flag,detx,dety,move_flag=testdef.together_line_circle1(cap)
            if line_flag==0 or move_flag==0:
                if line_flag ==1:   #直线到位则后续角度一直为0
                    theta=0
                if move_flag ==1:   #圆环到位则后续xy一直为0
                    detx=0
                    dety=0
                testdef.sendMessage5(ser,theta,detx,dety)
        print("together okokokokokokokokok line_flag:",line_flag,"move_flag:",move_flag)
        testdef.sendMessage(ser,68)  #发送到位信息
        time.sleep(0.01)
        move_flag=0  #标志位清零以便下次使用
        line_flag=0

        ####细调 先用颜色框确保能看见第五环 再用灰度houghcircles
        ####前三次精调 第四次码垛只做粗定位 以下程序会直接略过
        if circle_time<4:
            print("circle_time:",circle_time)
            if circle_time==1 or circle_time==2:
                circle_order=get_order
            elif circle_time==3:
                circle_order=put_order
            for i in range(3):
                print("iiiiiiiiiiiiii:",i,"color:",circle_order[i])
                # for j in range(3):
                #     x1_,y1_,img1_,flag11,detx1_p,dety1_p = testdef.circlePut_color(cap,circle_order[i])
                ####接收到爪子下降消息再开始进入细调
                recv_first=None
                while True:
                    recv_first=testdef.receiveMessage(ser)
                    print("recv_first",recv_first)
                    if recv_first==b'near ground':
                        break
                ####细调开始计时
                for j in range(2):
                    q=cap.grab()
                Time3=time.time()
                time_xi=6   #细调超时
                ####正常是6
                ####细调第一步 颜色定五环
                move_flag_color_1=0 
                while (not move_flag_color_1 and (time.time()-Time3)<time_xi):
                # while (not move_flag_color_1):
                # while((time.time()-Time3)<time_xi):
                    timee=time.time()
                    print("cccccccccccc")
                    # q=cap.grab()
                    x_,y_,img_,move_flag_color_1,detx_p,dety_p = testdef.circlePut_color(cap,circle_order[i])
                    if move_flag_color_1==0:    #flag=1后那次数据不需发送
                        testdef.sendMessage2(ser,detx_p,dety_p)
                        print("cutiao time:",time.time()-timee)
                print("xitiao11 okokokokokokokokok")
                move_flag_color_1=0   
                # #细调第二步 灰度定中心（第一版-无到位后二次检测
                # while (not move_flag_color_2 and (time.time()-Time3)<time_xi):
                # # while (not move_flag_color_2 ):
                #     print("xxxxxxxx")
                #     timeee=time.time()
                #     detx,dety,move_flag_color_2=testdef.circlePut1(cap)
                #     if move_flag_color_2==0:
                #         testdef.sendMessage2(ser,detx,dety)
                #         print("xitiao time:",time.time()-timeee)
                # print("xitiao22 okokokokokokokokok  move_flag_color_2:",move_flag_color_2)
                # if circle_order[i] == 1:
                #     testdef.sendMessage(ser,57)
                # elif circle_order[i] == 2:
                #     testdef.sendMessage(ser,64)
                # elif circle_order[i] == 3:
                #     testdef.sendMessage(ser,65)
                ####细调第二步 灰度定中心（第二版-到位后做二次检测-防止物料贴环边立即就放
                move_flag_color_2_2=0
                while (not move_flag_color_2_2 and (time.time()-Time3)<time_xi):
                # while (not move_flag_color_2_2 ):
                    print("xxxxxxxx")
                    timeee=time.time()
                    detx,dety,move_flag_color_2=testdef.circlePut1(cap)
                    testdef.sendMessage2(ser,detx,dety)
                    if move_flag_color_2==0:
                        # testdef.sendMessage2(ser,detx,dety)
                        print("xitiao time:",time.time()-timeee)
                    else:
                        # detxx=0
                        # detyy=0
                        flagg=0
                        time_check=2
                        ####初次到位后再看一次是否还在中心内 若在则到位 若不在则继续调整
                        for k in range(time_check):
                            detx2,dety2,move_flag_color_22=testdef.circlePut1(cap)
                            testdef.sendMessage2(ser,detx2,dety2)
                            # print("double check")
                            # detxx+=detx
                            # detyy+=dety
                            flagg+=move_flag_color_22
                            print("double check    flagg:",flagg)
                        if flagg==time_check:
                            move_flag_color_2_2=1
                            break
                print("xitiao22 okokokokokokokokok  move_flag_color_2:",move_flag_color_2)
                ####发送到位信息 根据颜色发送不同到位信息
                if circle_order[i] == 1:
                    testdef.sendMessage(ser,57)
                elif circle_order[i] == 2:
                    testdef.sendMessage(ser,64)
                elif circle_order[i] == 3:
                    testdef.sendMessage(ser,65)
                time.sleep(0.01)
                move_flag_color_2=0
                i = i+1  #继续下一个颜色
                
        circle_time +=1  #轮数+1
        recv=b'st'  #完成功能后进入空循环


####识别直线 在转盘旁调整车身
    elif recv==b'EE':
        while not cap.isOpened():
            print("Not open colorcap")
        ####开始计时
        Time_l=time.time()
        time_l=2
        ####调整车身姿态直到直线到位或超时
        while (not line_flag and (time.time()-Time_l)<time_l):
        # while (not line_flag):
            ####清理视频流缓存区
            for i in range(4):
                # theta1,line_flag1=testdef.detectLine(cap)
                ret=cap.grab()
            theta,line_flag=testdef.detectLine_gray(cap)
            if line_flag ==0:   #到位后当次偏差值不发送
                testdef.sendMessage5(ser,theta,0,0)
                print("main li de theta:",theta)
            # elif line_flag==1:
        print("line_flag:",line_flag)
        testdef.sendMessage(ser,39)
        time.sleep(0.01)
        testdef.sendMessage(ser,40)
        time.sleep(0.01)
        testdef.sendMessage(ser,68)

        line_flag=0
        recv=b'st'   #进入空循环

    #############################################################################################
    ##############################决赛功能备用代码################################################
    #############################################################################################

####stm32接收消息时（wifi）处理数据
    elif recv==b'MM':
        while True:
            recv_order=testdef.receiveMessage(ser)
            print(recv_order)
            if recv_order:
                data=recv_order
                break
        data=data.decode("utf8")
        data1 = data[0:3]
        data2 = data[4:7]
        # print("data1",data1)
        # print("data2",data2)
        get_order=testdef.sort(data1)
        put_order=testdef.sort(data2)
        order=get_order+put_order
        #信息发送给stm32
        testdef.sendMessage3(ser,order)
        time.sleep(0.01)
        testdef.sendMessage3(ser,order)
        time.sleep(0.01)
        testdef.sendMessage3(ser,order)
        recv=b'st'
    

####识别转盘 夹取物料（夹完在物料盘处二次检查 次次检查（如三棱柱物料，没夹到仍在爪子下方，无法在转盘处直接检查
    elif recv==b'NN':      
        while not cap.isOpened():
            print("Not open colorcap")
        #根据运行轮数使用不同顺序
        if plate_time == 1:
            plate_order=get_order
        elif plate_time == 2:
            plate_order=put_order
        # plate_order=get_order
        print("plate_order:",plate_order)
        stop_flag=0
        i=0
        while i<3:
        #依据颜色顺序循环处理3个物料
            # print("iii:",i)
            # flagno = testdef.detectPlate(cap, 1)
            while not stop_flag:
                print("i:",i)
                flag2 = testdef.detectPlate(cap,plate_order[i])
                x_,y_,img_,flag1,detx,dety = testdef.findBlockCenter(cap,plate_order[i])
                #当所看对应颜色物料静止时
                if  (flag2 == 1 and flag1 == 1):
                    # testdef.updateCorrectxy(cap,plate_order[i])
                    x_,y_,img_,flag1,detx,dety = testdef.findBlockCenter(cap,plate_order[i])
                    print("detx:",detx,"dety:",dety,"flag1:",flag1)
                    stop_flag = plate_order[i]  #令标志位为颜色序号
                    print("stop_flag",stop_flag)
                    testdef.sendMessage2(ser,detx,dety)  #给机械臂发送大致调整参数
                    time.sleep(0.01)
                    if stop_flag == 1:  #发送到位信息
                        testdef.sendMessage(ser,7)
                    elif stop_flag == 2:
                        testdef.sendMessage(ser,8)
                    elif stop_flag == 3:
                        testdef.sendMessage(ser,9)
                    # testdef.sendMessage(ser,stop_flag)
            Time = time.time()
            stop_flag=0
            flag_check=0
            time_plate_check=6.2
            #每次转到物料盘后检查
            # if i == 0:
            while (not flag_check) and ((time.time()-Time)<time_plate_check):
                recv_check=testdef.receiveMessage(ser)
                print("recv_check",recv_check)
                if recv_check==b'check':
                    print("start checkkkkkkkkkkkkkkkkkkk")
                    flag_check=testdef.detectPlate_check(cap,plate_order[i])
                    print("flag_chexk:",flag_check)
                    if flag_check :  #如果夹到了继续下一个颜色
                        print("next colorrrrrrrrrrrrrrrrrrrr")
                        i=i+1
                    else:  #没夹到仍等待第一个
                        testdef.sendMessage(ser,3)
                        flag_check=1
                    # break
            if not flag_check:
                i+=1
            # # Time1=time.time()
            # # print("Time1:",Time1)
            # # time.sleep(0.5)
            # print("start checkkkkkkkkkkkkkkkkkkk")
            # flag_check=testdef.detectPlate_check(cap,plate_order[i])
            # # Time2=time.time()-Time1
            # # print("Time2:",Time2)
            # print("flag_chexk:",flag_check)
            # if flag_check :  #如果夹到了继续下一个颜色
            #     print("next colorrrrrrrrrrrrrrrrrrrr")
            #     i=i+1
            # else:  #没夹到仍等待第一个
            #     testdef.sendMessage(ser,3)
            # # else :
            # #     time.sleep(3)
            # #     i=i+1
            # # time.sleep(3)
            # # i=i+1
        # plate_time += 1  #轮数+1
        cv2.destroyAllWindows()
        recv=b'st'


####识别转盘 放置物料 转盘是色块
    elif recv==b'HH':
        i=0
        while not cap.isOpened():
            print("Not open colorcap")
        # if plate_time == 1:
        #     plate_order=get_order
        # elif plate_time == 2:
        #     plate_order=put_order
        plate_order=get_order
        print("plate_order:",plate_order)
        stop_flag=0
        # i=0
        stop_flag_1=0
        stop_first=0
        x_last=0
        y_last=0
        while not stop_first:
            flag2 = testdef.detectPlate_gray(cap)
            x_,y_,img_,flag1,detx,dety,color = testdef.findBlockCenter_gray(cap)
            if  (flag2 == 1 and flag1 == 1):
                x_last=x_
                y_last=y_
                while not stop_first:
                    x_,y_,img_,flag_,detx_,dety_,color_number= testdef.findBlockCenter_gray(cap)
                    if abs(x_last-x_)<0.05 and abs(y_last-y_)<0.05:
                        print("1")
                        x_last=x_
                        y_last=y_
                    else:
                        stop_first=1
        print("kaishidongjixiebi kaishidongjixiebi")
        while not stop_flag_1:
            # print("i:",i)
            # if stop_flag_1==0:
            flag2 = testdef.detectPlate_gray(cap)
            x_,y_,img_,flag1,detx,dety,color = testdef.findBlockCenter_gray(cap)
            if  (flag2 == 1 and flag1 == 1):
            # if flag2==1: 
                time_start=time.time()
                while (not stop_flag_1 and (time.time()-time_start)<3.2):
                    x_,y_,img_,flag9,detx9,dety9,color = testdef.findBlockCenter_gray(cap)
                    print("qqqqqqqq:",abs(detx9),abs(dety9))
                    # if abs(detx9)<12 and abs(dety9)<12 and detx9!=0 and dety9!=0:
                    if abs(detx9)<12 and abs(dety9)<12 and flag9==1:
                        stop_flag_1=1
                        print("stop_flag_1:",stop_flag_1)
                    else:
                        testdef.sendMessage2(ser,detx9,dety9)
                        time.sleep(0.01)
                if stop_flag_1==1:
                    testdef.sendMessage(ser,16)
                    time.sleep(4)
                else:
                    print("chaoshilechaoshilechaoshilechaoshile")
                    time.sleep(2)
        while i<3:
            while not stop_flag:
                print("i:",i)
            #     # if stop_flag_1==0:
                flag2 = testdef.detectPlate(cap,plate_order[i])
                x_,y_,img_,flag1,detx,dety = testdef.findBlockCenter(cap,plate_order[i])
                if  (flag2 == 1 and flag1 == 1):
                    # stop_flag=plate_order[i]
                    # if color==plate_order[i]:
                        stop_flag=1
                        if plate_order[i] == 1:
                            testdef.sendMessage(ser,7)
                        elif plate_order[i] == 2:
                            testdef.sendMessage(ser,8)
                        elif plate_order[i]== 3:
                            testdef.sendMessage(ser,9)
                    # testdef.sendMessage(ser,stop_flag)
            # Time = time.time()
            stop_flag=0
            stop_flag_1=0
            time.sleep(2)
            i=i+1
        plate_time += 1
        cv2.destroyAllWindows()
        recv=b'st'


####识别转盘 放置物料 转盘是圆环 （可行性和转盘转速紧密相关
    elif recv==b'LL':    
        i=0
        while not cap.isOpened():
            print("Not open colorcap")
        # if plate_time == 1:
        #     plate_order=get_order
        # elif plate_time == 2:
        #     plate_order=put_order
        plate_order=get_order
        print("plate_order:",plate_order)
        stop_flag=0
        # i=0
        stop_flag_1=0
        stop_first=0
        x_last=0
        y_last=0
        turn_direction=0
        detx_1,dety_1=0,0
        while not stop_first:
            flag2 = testdef.detectPlate_gray(cap)
            x_,y_,img_,flag1,detx,dety,color = testdef.findBlockCenter_gray(cap)
            if  (flag2 == 1 and flag1 == 1):
                x_last=x_
                y_last=y_
                while not stop_first:
                    x_,y_,img_,flag_,detx_,dety_,color_number= testdef.findBlockCenter_gray(cap)
                    if abs(x_last-x_)<0.05 and abs(y_last-y_)<0.05:
                        print("1")
                        x_last=x_
                        y_last=y_
                    else:
                        stop_first=1
                        detx_1,dety_1=detx_,dety_
                        if x_-x_last<0:
                            turn_direction=1  #left
                            print("turn left  ++++++")
                        elif x_-x_last>0:
                            turn_direction=2  #right
                            print("turn right  ------")
        print("kaishidongjixiebi kaishidongjixiebi")
        testdef.sendMessage(ser,97) #回去夹物料
        time.sleep(0.05)
        testdef.sendMessage2(ser,detx_1,dety_1)
        print("daoweipianchazhi")

        plate_wait=1
        if plate_order==[1,3,2] or plate_order==[2,1,3] or plate_order==[3,2,1]:  
        #↑转盘上颜色顺时针为1,3,2 单独看转盘无论转动方向
        # if plate_order==[1,2,3] or plate_order==[2,3,1] or plate_order==[3,1,2]:
        ##颜色顺时针为1,2,3
            plate_wait=-1
        if turn_direction==2:
            plate_wait=-plate_wait
        
        print("plate_wait:",plate_wait)
        time_det=0
        for i in range(3):
            print("iiiiiiiiiiiiii:",i,"color:",plate_order[i])
            # recv_first=None
            # for j in range(3):
            #     x1_,y1_,img1_,flag11,detx1_p,dety1_p = testdef.circlePut_color(cap,circle_order[i])
            # for k in range(2):
            q=cap.grab()
            while True:
                flag2 = testdef.detectPlate_circle(cap,plate_order[i])
                x_,y_,img_,flag1= testdef.findBlockCenter_circle(cap,plate_order[i])
                if  (flag2 == 1 and flag1 == 1):
                    if plate_wait==-1:
                        if i==0:
                            time_1=time.time()
                            print("time_1:",time_1)
                        elif i==1:
                            time_det=(time.time()-time_1)/2
                            print(time.time()-time_1,"time_det:",time_det)
                    break
            Time3=time.time()
            time_xi=2.4
            q=cap.grab()
            print("daoweipianchazhi11111111111111111111111111111111111111111111")
            while (not move_flag_color_1 and (time.time()-Time3)<time_xi):
            # while (not move_flag_color_1):
                # timee=time.time()
                print("cccccccccccc")
                x_,y_,img_,move_flag_color_1,detx_p,dety_p = testdef.circlePut_color(cap,plate_order[i])
                if move_flag_color_1==0:
                    testdef.sendMessage2(ser,detx_p,dety_p)
                    # print("cutiao time:",time.time()-timee)
            print("xitiao11 okokokokokokokokok")
            move_flag_color_1=0   
            #�ڶ�����ϸ��
            # while (not move_flag_color_2 and (time.time()-Time3)<time_xi):
            q=cap.grab()
            while ((time.time()-Time3)<time_xi ):
                print("xxxxxxxx")
                # timeee=time.time()
                detx,dety,move_flag_color_2=testdef.circlePut1(cap)
                if move_flag_color_2==0:
                    testdef.sendMessage2(ser,detx,dety)
                    # print("xitiao time:",time.time()-timeee)

            print("xitiao22 okokokokokokokokok  move_flag_color_2:",move_flag_color_2)
            if plate_order[i] == 1:
                testdef.sendMessage(ser,57)
            elif plate_order[i] == 2:
                testdef.sendMessage(ser,64)
            elif plate_order[i]== 3:
                testdef.sendMessage(ser,65)
            time.sleep(0.01)
            if i==1:
                if time_det != 0:
                    time_det+=1
                print("wait for 3 time_det:",time_det)
                time.sleep(time_det)
                testdef.sendMessage(ser,98)
            move_flag_color_2=0
            i = i+1
        plate_time += 1
        # cv2.destroyAllWindows()
        recv=b'st'


####在一条直线三个圆环处夹取物料 用于判定位置和颜色对应关系
    elif recv==b'II':
        while not cap.isOpened():
            print("Not open colorcap")
        #开始计时
        Time_l=time.time()
        time_l=6
        #调整车身姿态直到直线到位或超时
        while (not line_flag and (time.time()-Time_l)<time_l):
        # while (not line_flag ):
            #清理视频流缓存区
            for i in range(4):
                # theta1,line_flag1=testdef.detectLine(cap)
                ret=cap.grab()
            theta,line_flag=testdef.detectLine(cap)
            if line_flag ==0:
                testdef.sendMessage5(ser,theta,0,0)
                print("main li de theta:",theta)
            # elif line_flag==1:
        print("line_flag:",line_flag)
        testdef.sendMessage(ser,39)
        time.sleep(0.01)
        testdef.sendMessage(ser,40)
        time.sleep(0.01)
        testdef.sendMessage(ser,68)
        line_flag=0        
        while True:
            recv_first=testdef.receiveMessage(ser)
            print("recv_first",recv_first)
            if recv_first==b'near ground':
                break
        color_2=0
        flag1=0
        while not flag1:
            x_,y_,img_,flag1,detx,dety,color_2= testdef.findBlockCenter_get(cap)
            if  (flag1 == 0):
                testdef.sendMessage5(ser,0,detx,dety)
        testdef.sendMessage(ser,68)
        flag1=0
        while True:
            recv_first=testdef.receiveMessage(ser)
            print("recv_first",recv_first)
            if recv_first==b'near ground':
                break

        color_1=0
        for i in range(2):
            x_,y_,img_,flag2,detx,dety,color= testdef.findBlockCenter_get(cap)
        x_,y_,img_,flag2,detx,dety,color_1= testdef.findBlockCenter_get(cap)
        get_order_blank.append(color_1)

        get_order_blank.append(color_2)
        color_3=6-color_1-color_2
        get_order_blank.append(color_3)

        testdef.sendMessage6(ser,get_order_blank)

        recv=b'st'
        get_order_blank=[]
        

####测试路径时 只用在圆环处粗调的功能
    elif recv==b'JJ':       
        print("cccccccccccc")
        print("line_flag===",line_flag,"move_flag===",move_flag)
        while not cap.isOpened():
            print("Not open colorcap")
        for i in range(2):
            q=cap.grab()
        #粗调 圆环粗定位和直线一起调整
        #粗调开始计时
        Time_test=time.time()   
        time_together=7
        #发送偏差值信息调整车身位置直到超时或者直线圆环均到位
        while ((time.time()-Time_test)<time_together) and ((not line_flag) or (not move_flag)) :
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
        testdef.sendMessage(ser,68)  #发送到位信息
        time.sleep(0.01)
        move_flag=0  #标志位清零以便下次使用
        line_flag=0

        recv=b'st'


####识别圆环 放置物料（物料夹不紧时，更新偏差值
    elif recv==b'KK':       
        print("cccccccccccc")
        print("line_flag===",line_flag,"move_flag===",move_flag)
        while not cap.isOpened():
            print("Not open colorcap")
        for i in range(2):
            q=cap.grab()
        #粗调 圆环粗定位和直线一起调整
        #粗调开始计时
        Time1=time.time()   
        time_together=7
        #发送偏差值信息调整车身位置直到超时或者直线圆环均到位
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
        testdef.sendMessage(ser,68)  #发送到位信息
        time.sleep(0.01)
        move_flag=0  #标志位清零以便下次使用
        line_flag=0

        #细调 先用颜色框确保能看见第五环 再用灰度houghcircles
        #前三次精调 第四次码垛只做粗定位 以下程序会直接略过
        # if circle_time < 5 :
        if circle_time<4:
            print("circle_time:",circle_time)
            if circle_time==1 or circle_time==2:
                circle_order=get_order
            elif circle_time==3:
            # elif circle_time==3 or circle_time==4:
                circle_order=put_order
            # circle_order=get_order
            for i in range(3):
                print("iiiiiiiiiiiiii:",i,"color:",circle_order[i])
                recv_first=None
                recv_update=None
                # for j in range(3):
                #     x1_,y1_,img1_,flag11,detx1_p,dety1_p = testdef.circlePut_color(cap,circle_order[i])
                #接收到爪子下降消息再开始进入细调
                q=cap.grab()
                while True:
                    recv_update=testdef.receiveMessage(ser)
                    print("recv_update",recv_update)
                    if recv_update==b'update':#??????????????????
                        time_update=time.time()
                        testdef.updateCorrectxy(cap,circle_order[i])
                        print("update center time:",time.time()-time_update)
                        break
                while True:
                    recv_first=testdef.receiveMessage(ser)
                    print("recv_first",recv_first)
                    if recv_first==b'near ground':
                        break
                #细调开始计时
                for j in range(2):
                    q=cap.grab()
                Time3=time.time()
                time_xi=6
                #正常是6
                #细调第一步 颜色定五环
                while (not move_flag_color_1 and (time.time()-Time3)<time_xi):
                # while (not move_flag_color_1):
                # while((time.time()-Time3)<time_xi):
                    timee=time.time()
                    print("cccccccccccc")
                    recv1=testdef.receiveMessage(ser)
                    print("                        recvrecvrecvrecv:",recv1)
                    # q=cap.grab()
                    x_,y_,img_,move_flag_color_1,detx_p,dety_p = testdef.circlePut_color(cap,circle_order[i])
                    if move_flag_color_1==0:
                        testdef.sendMessage2(ser,detx_p,dety_p)
                        print("cutiao time:",time.time()-timee)
                print("xitiao11 okokokokokokokokok")
                move_flag_color_1=0   
                # #细调第二步 灰度定中心（第一版-无到位后二次检测
                # while (not move_flag_color_2 and (time.time()-Time3)<time_xi):
                # # while (not move_flag_color_2 ):
                #     print("xxxxxxxx")
                #     timeee=time.time()
                #     detx,dety,move_flag_color_2=testdef.circlePut1(cap)
                #     if move_flag_color_2==0:
                #         testdef.sendMessage2(ser,detx,dety)
                #         print("xitiao time:",time.time()-timeee)
                # print("xitiao22 okokokokokokokokok  move_flag_color_2:",move_flag_color_2)
                # if circle_order[i] == 1:
                #     testdef.sendMessage(ser,57)
                # elif circle_order[i] == 2:
                #     testdef.sendMessage(ser,64)
                # elif circle_order[i] == 3:
                #     testdef.sendMessage(ser,65)
                #细调第二步 灰度定中心（第二版-到位后做二次检测-防止物料贴环边立即就放
                move_flag_color_2_2=0
                while (not move_flag_color_2_2 and (time.time()-Time3)<time_xi):
                # while (not move_flag_color_2_2 ):
                    print("xxxxxxxx")
                    recv2=testdef.receiveMessage(ser)
                    print("                        recvrecvrecvrecv22222:",recv2)
                    timeee=time.time()
                    detx,dety,move_flag_color_2=testdef.circlePut1(cap)
                    testdef.sendMessage2(ser,detx,dety)
                    if move_flag_color_2==0:
                        # testdef.sendMessage2(ser,detx,dety)
                        print("xitiao time:",time.time()-timeee)
                    else:
                        detxx=0
                        detyy=0
                        flagg=0
                        time_check=2
                        #初次到位后再看一次是否还在中心内 若在则到位 若不在则继续调整
                        for k in range(time_check):
                            detx2,dety2,move_flag_color_22=testdef.circlePut1(cap)
                            # testdef.sendMessage2(ser,detx2,dety2)
                            # print("double check")
                            detxx+=detx
                            detyy+=dety
                            flagg+=move_flag_color_22
                            print("double check    flagg:",flagg)
                        if flagg==time_check:
                            move_flag_color_2_2=1
                            break
                print("xitiao22 okokokokokokokokok  move_flag_color_2:",move_flag_color_2)
                #发送到位信息 根据颜色发送不同到位信息
                if circle_order[i] == 1:
                    testdef.sendMessage(ser,57)
                elif circle_order[i] == 2:
                    testdef.sendMessage(ser,64)
                elif circle_order[i] == 3:
                    testdef.sendMessage(ser,65)
                time.sleep(0.01)
                move_flag_color_2=0
                i = i+1  #继续下一个颜色
                
            circle_time +=1  #轮数+1


        # cv2.destroyAllWindows()
        testdef.defaltCorrectxy()
        recv=b'st'  #完成功能后进入空循环


####/没在用/ only gray
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


    #############################################################################################
    ####################################模拟赛使用################################################
    #############################################################################################

####模拟使用--夹取物料
    elif recv==b'OO':       
        print("cccccccccccc")
        print("line_flag===",line_flag,"move_flag===",move_flag)
        while not cap.isOpened():
            print("Not open colorcap")
        for i in range(2):
            q=cap.grab()
        #粗调 圆环粗定位和直线一起调整
        #粗调开始计时
        Time1=time.time()   
        time_together=7
        #发送偏差值信息调整车身位置直到超时或者直线圆环均到位
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
        testdef.sendMessage(ser,68)  #发送到位信息
        time.sleep(0.01)
        move_flag=0  #标志位清零以便下次使用
        line_flag=0

        #细调 先用颜色框确保能看见第五环 再用灰度houghcircles
        #前三次精调 第四次码垛只做粗定位 以下程序会直接略过
        # if circle_time < 5 :
        if circle_time<3:
            print("circle_time:",circle_time)
            if circle_time==1:
                circle_order=get_order
            elif circle_time==2:
            # elif circle_time==3 or circle_time==4:
                circle_order=put_order
            # circle_order=get_order
            for i in range(3):
                print("iiiiiiiiiiiiii:",i,"color:",circle_order[i])
                recv_first=None
                # for j in range(3):
                #     x1_,y1_,img1_,flag11,detx1_p,dety1_p = testdef.circlePut_color(cap,circle_order[i])
                #接收到爪子下降消息再开始进入细调
                while True:
                    recv_first=testdef.receiveMessage(ser)
                    print("recv_first",recv_first)
                    if recv_first==b'near ground':
                        break
                #细调开始计时
                for j in range(2):
                    q=cap.grab()
                Time3=time.time()
                time_xi=2
                #正常是6
                #细调第一步 颜色定五环
                while (not move_flag_color_1 and (time.time()-Time3)<time_xi):
                # while (not move_flag_color_1):
                # while((time.time()-Time3)<time_xi):
                    timee=time.time()
                    print("cccccccccccc")
                    recv1=testdef.receiveMessage(ser)
                    print("                        recvrecvrecvrecv:",recv1)
                    # q=cap.grab()
                    x_,y_,img_,move_flag_color_1,detx_p,dety_p = testdef.circlePut_color(cap,circle_order[i])
                    if move_flag_color_1==0:
                        testdef.sendMessage2(ser,detx_p,dety_p)
                        print("cutiao time:",time.time()-timee)
                print("xitiao11 okokokokokokokokok")
                move_flag_color_1=0   
                #细调第二步 灰度定中心（第一版-无到位后二次检测
                move_flag_color_2=0
                while (not move_flag_color_2 and (time.time()-Time3)<time_xi):
                # while (not move_flag_color_2 ):
                    print("xxxxxxxx")
                    # timeee=time.time()
                    detx,dety,move_flag_color_2=testdef.circlePut1(cap)
                    if move_flag_color_2==0:
                        testdef.sendMessage2(ser,detx,dety)
                        # print("xitiao time:",time.time()-timeee)
                print("xitiao22 okokokokokokokokok  move_flag_color_2:",move_flag_color_2)
                if circle_order[i] == 1:
                    testdef.sendMessage(ser,57)
                elif circle_order[i] == 2:
                    testdef.sendMessage(ser,64)
                elif circle_order[i] == 3:
                    testdef.sendMessage(ser,65)
                # #细调第二步 灰度定中心（第二版-到位后做二次检测-防止物料贴环边立即就放
                # move_flag_color_2_2=0
                # while (not move_flag_color_2_2 and (time.time()-Time3)<time_xi):
                # # while (not move_flag_color_2_2 ):
                #     print("xxxxxxxx")
                #     recv2=testdef.receiveMessage(ser)
                #     print("                        recvrecvrecvrecv22222:",recv2)
                #     timeee=time.time()
                #     detx,dety,move_flag_color_2=testdef.circlePut1(cap)
                #     testdef.sendMessage2(ser,detx,dety)
                #     if move_flag_color_2==0:
                #         # testdef.sendMessage2(ser,detx,dety)
                #         print("xitiao time:",time.time()-timeee)
                #     else:
                #         detxx=0
                #         detyy=0
                #         flagg=0
                #         time_check=2
                #         #初次到位后再看一次是否还在中心内 若在则到位 若不在则继续调整
                #         for k in range(time_check):
                #             detx2,dety2,move_flag_color_22=testdef.circlePut1(cap)
                #             # testdef.sendMessage2(ser,detx2,dety2)
                #             # print("double check")
                #             detxx+=detx
                #             detyy+=dety
                #             flagg+=move_flag_color_22
                #             print("double check    flagg:",flagg)
                #         if flagg==time_check:
                #             move_flag_color_2_2=1
                #             break
                # print("xitiao22 okokokokokokokokok  move_flag_color_2:",move_flag_color_2)
                # #发送到位信息 根据颜色发送不同到位信息
                # if circle_order[i] == 1:
                #     testdef.sendMessage(ser,57)
                # elif circle_order[i] == 2:
                #     testdef.sendMessage(ser,64)
                # elif circle_order[i] == 3:
                #     testdef.sendMessage(ser,65)
                time.sleep(0.01)
                move_flag_color_2=0
                i = i+1  #继续下一个颜色
                
            circle_time +=1  #轮数+1
        recv=b'st'  #完成功能后进入空循环


####模拟使用--放置物料--转盘圆环上放物料--先调整至准确位置，然后看颜色直接放三次
    elif recv==b'PP':
        i=0
        while not cap.isOpened():
            print("Not open colorcap")
        if plate_time == 1:
            plate_order=get_order
        elif plate_time == 2:
            plate_order=put_order
        # plate_order=get_order
        print("plate_order:",plate_order)
        stop_flag=0
        # i=0
        stop_flag_1=0
        stop_first=0
        x_last=0
        y_last=0
        turn_direction=0
        while not stop_first:
            flag2 = testdef.detectPlate_gray(cap)
            x_,y_,img_,flag1,detx,dety,color = testdef.findBlockCenter_gray(cap)
            if  (flag2 == 1 and flag1 == 1):
                x_last=x_
                y_last=y_
                while not stop_first:
                    x_,y_,img_,flag_,detx_,dety_,color_number= testdef.findBlockCenter_gray(cap)
                    if abs(x_last-x_)<0.05 and abs(y_last-y_)<0.05:
                        print("1")
                        x_last=x_
                        y_last=y_
                    else:
                        stop_first=1
                        detx_1,dety_1=detx_,dety_
                        if x_-x_last<0:
                            turn_direction=1  #left
                            print("turn left  ++++++")
                        elif x_-x_last>0:
                            turn_direction=2  #right
                            print("turn right  ------")
        print("kaishidongjixiebi kaishidongjixiebi")

        plate_wait=1
        if plate_order==[1,3,2] or plate_order==[2,1,3] or plate_order==[3,2,1]:  
        #↑转盘上颜色顺时针为1,3,2 单独看转盘无论转动方向
        # if plate_order==[1,2,3] or plate_order==[2,3,1] or plate_order==[3,1,2]:
        ##颜色顺时针为1,2,3
            plate_wait=-1
        if turn_direction==2:
            plate_wait=-plate_wait
        print("plate_wait:",plate_wait)

        time_det=0
        time_over=0
        while (not stop_flag_1) or (time_over<2):
            # print("i:",i)
            # if stop_flag_1==0:
            flag2 = testdef.detectPlate_gray(cap)
            x_,y_,img_,flag1,detx,dety,color = testdef.findBlockCenter_gray(cap)
            if  (flag2 == 1 and flag1 == 1):
                if plate_wait==-1:
                    if time_over==0:
                        time_1=time.time()
                        print("time_1:",time_1)
                    elif time_over==1:
                        time_det=(time.time()-time_1)
                        print(time.time()-time_1,"time_det:",time_det)
                time_over+=1
                
                time_start=time.time()
                while (not stop_flag_1 and (time.time()-time_start)<3):
                    x_,y_,img_,flag9,detx9,dety9,color = testdef.findBlockCenter_gray(cap)
                    print("qqqqqqqq:",abs(detx9),abs(dety9))
                    # if abs(detx9)<12 and abs(dety9)<12 and detx9!=0 and dety9!=0:
                    if abs(detx9)<4 and abs(dety9)<4 and flag9==1:
                        stop_flag_1=1
                        print("stop_flag_1:",stop_flag_1)
                    else:
                        testdef.sendMessage2(ser,detx9,dety9)
                        time.sleep(0.01)
                if stop_flag_1==1 and time_over<2:
                    time.sleep(4)###########？？？
                elif stop_flag_1==0:
                    print("chaoshilechaoshilechaoshilechaoshile")
                    time.sleep(2)

        testdef.sendMessage(ser,57)

        while i<3:
            x_last_1=0
            y_last_1=0
            while not stop_flag:
                print("i:",i)
                flag2 = testdef.detectPlate_circle(cap,plate_order[i])
                x_,y_,img_,flag1= testdef.findBlockCenter_circle(cap,plate_order[i])
                if  (flag2 == 1 and flag1 == 1):
                    # stop_flag=1
                    testdef.sendMessage(ser,51)
                    if i<2:
                        x_last_1=x_
                        y_last_1=y_
                        while not stop_flag:
                            x_,y_,img_,flag11= testdef.findBlockCenter_circle(cap,plate_order[i])
                            print("x_,y_:",x_,y_)
                            if flag11==1:
                                if abs(x_last_1-x_)<0.05 and abs(y_last_1-y_)<0.05:
                                    print("111")
                                    x_last_1=x_
                                    y_last_1=y_
                                    flag11=0
                                else:
                                    print("222")
                                    stop_flag=1
                                    testdef.sendMessage(ser,98)
                    elif i==2:
                        stop_flag=1

            if i==1:
                if time_det != 0:
                    time_det-=2
                print("wait for 3 time_det:",time_det)
                while True:
                    recv_wait=testdef.receiveMessage(ser)
                    print("recv_wait",recv_wait)
                    if recv_wait==b'wait':
                        break
                time.sleep(time_det)
                # time.sleep(5)
                testdef.sendMessage(ser,98)
            stop_flag=0
            stop_flag_1=0
            # time.sleep(2)
            i=i+1
        plate_time += 1
        cv2.destroyAllWindows()
        recv=b'st'


    #############################################################################################
    #################################空循环及清零部分#############################################
    #############################################################################################

####待机状态
    elif recv==b'st':
        pass

####全局标志位清零 可直接开始第二轮
    elif recv==b'end':
        print("endendendendnendnendnendne")
        cv2.destroyAllWindows()
        ####初始化侧边二维码摄像头
        # # global code_cap
        code_cap = cv2.VideoCapture("/dev/code_video1",cv2.CAP_V4L2)  
        code_cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        code_cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
        code_cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
        code_cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
        if  not code_cap.isOpened():
            print("faillllllllll")
        ####初始化各个变量
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
        # recv = b'HH'
        recv=''
        line_cishu =1
        get_order=[3,1,2]
        # get_order=[1,2,3]
        get_order_blank=[]
        recv=b'st'

    if cv2.waitKey(20) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()

