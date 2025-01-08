import cv2
import numpy as np
import math
import time
import serial 
import testdef


# Bus 003 Device 002: ID 0c45:6340 Microdia Camera       uppp

frameWidth = 640
frameHeight = 480
global cap
cap = cv2.VideoCapture("/dev/up_video",cv2.CAP_V4L2)
cap.set(3, frameWidth)
cap.set(4, frameHeight)
cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
cap.set(cv2.CAP_PROP_EXPOSURE, float(0.2)) 
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

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
# recv = '05'
recv=''
line_cishu =1
while True:
    # get_order=[2,2,2]
    # recv = '00'

    recv_mess = testdef.receiveMessage(ser)
    if recv_mess != None:
        print("recv_mess:",recv_mess)
    if recv_mess != None:
        if recv_mess == b'AA' or recv_mess==b'BB' or recv_mess==b'CC' or recv_mess==b'DD' or recv_mess==b'EE' or recv_mess==b'FF' or recv_mess==b'GG' or recv_mess==b'st':
            recv=recv_mess
    # print("first  recv:",recv)
    print(recv)


    if recv==b'AA':     #shibie code
        # code_cap = cv2.VideoCapture("/dev/code_video",cv2.CAP_V4L2)  
        # code_cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        # code_cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)


        # su,fr=cap.read()
        # cv2.imshow("up",fr)p

        while True:
            # su,fr=code_cap.read()
            # cv2.imshow("up",fr)
            # print(su)
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
        cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
        cap.set(3, 640)
        cap.set(4, 480)
        cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        cap.set(cv2.CAP_PROP_EXPOSURE, float(0.2)) 
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        

        recv=b'st'


    #Բ�̴�ץ���
    elif recv==b'BB':      #shibie zhuanpan
        while not cap.isOpened():
            print("Not open colorcap")
        stop_flag=0
        for i in range(3):
            # flagno = testdef.detectPlate(cap, 1)
            while not stop_flag:
                recv0=testdef.receiveMessage(ser)
                if recv0 != None:
                    print("00000000000recv0000:",recv0)
                flag2 = testdef.detectPlate(cap,get_order[i])
                x_,y_,img_,flag1 = testdef.findBlockCenter(cap,get_order[i])
                if  (flag2 == 1 and flag1 == 1):
                    stop_flag = get_order[i]
                    print("stop_flag",stop_flag)
                    if stop_flag == 1:
                        testdef.sendMessage(ser,7)
                    elif stop_flag == 2:
                        testdef.sendMessage(ser,8)
                    elif stop_flag == 3:
                        testdef.sendMessage(ser,9)
                    # testdef.sendMessage(ser,stop_flag)
            stop_flag=0
            time.sleep(3)
            i=i+1
        cv2.destroyAllWindows()
        recv=b'st'

        
   
    #Բ������λ���գ�
    elif recv==b'CC':       #shibie yuanhuan
        print("cccccccccccc")
        print("line_flag===",line_flag,"move_flag===",move_flag)
        while not cap.isOpened():
            print("Not open colorcap")
        # if(line_cishu == 2 or line_cishu ==4):
        while not line_flag:
            theta,line_flag=testdef.detectLine(cap)
            if line_flag ==0:
                testdef.sendMessage4(ser,theta)
                print("main li de theta:",theta)
            elif line_flag==1:
                print("line_flag:",line_flag)
                testdef.sendMessage(ser,39)
                time.sleep(0.01)
                testdef.sendMessage(ser,40)
                break
        # # cv2.destroyAllWindows()
        while not move_flag:
            recvv=testdef.receiveMessage(ser)
            print(recvv)
            if recvv!=None:
                recv=b'st'
                line_flag=0
                print("recv=",recv,"line_flag=",line_flag)
                print("outttttttttttttttttttttttttttttttttttt")
                break
            recv0=testdef.receiveMessage(ser)
            for i in range(5):
                detxq,detyq,move_dirq,move_flagq=testdef.findCountours(cap)
            detx,dety,move_dir,move_flag=testdef.findCountours(cap)
            if recv0 != None:
                    print("00000000000recv0000:",recv0)
            if move_flag==0:
                testdef.sendMessage2(ser,detx,dety)
            elif move_flag==1:                          
                print("move_flag:",move_flag)
                # testdef.sendMessage(ser,23)
                # time.sleep(0.1)
                # testdef.sendMessage(ser,23)                
                # time.sleep(0.1)
                testdef.sendMessage(ser,23)
                time.sleep(0.01)
                testdef.sendMessage(ser,24)
                # time.sleep(0.1)
                # testdef.sendMessage(ser,24)
                # time.sleep(0.1)
                # testdef.sendMessage(ser,24)
            
                # move_flag=0
            
                break
        move_flag=0
        line_flag=0
        recv=b'st'
        line_cishu+=1
        # cv2.destroyAllWindows()
        

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
        while not line_flag:
            # for i in range(5):
            #     theta1,line_flag1=testdef.detectLine(cap)
            theta,line_flag=testdef.detectLine(cap)
            if line_flag ==0:
                testdef.sendMessage4(ser,theta)
                print("main li de theta:",theta)
            elif line_flag==1:
                print("line_flag:",line_flag)
                # testdef.sendMessage(ser,39)
                # time.sleep(0.01)
                # testdef.sendMessage(ser,39)
                # time.sleep(0.01)
                testdef.sendMessage(ser,39)
                time.sleep(0.01)
                testdef.sendMessage(ser,40)
                # time.sleep(0.01)
                # testdef.sendMessage(ser,40)
                # time.sleep(0.01)
                # testdef.sendMessage(ser,40)
                # time.sleep(0.01)
                break
        line_flag=0
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

    #color+gray
    elif recv==b'GG':
        # while not move_flag_color:
        while True:
            print("iiiiiiiiiiinnnnnnnnnnnnnnnn")
            for j in range(3):
                ret=cap.grab()
            x_,y_,img_,flag1,detx_p,dety_p = testdef.circlePut_color(cap,2)
            if abs(detx_p)<12 and abs(dety_p)<12:
                move_flag_color=1
                break
            else:
                testdef.sendMessage2(ser,detx_p,dety_p)
        move_flag_color=0
        while not move_flag:
            # recvv=testdef.receiveMessage(ser)
            # print(recvv)
            # if recvv!=None:
            #     recv=b'st'
            #     line_flag=0
            #     print("recv=",recv,"line_flag=",line_flag)
            #     print("outttttttttttttttttttttttttttttttttttt")
            #     break
            for j in range(3):
                ret=cap.grab()
            detx,dety,move_flag=testdef.circlePut1(cap)
            if move_flag==0:
                testdef.sendMessage2(ser,detx,dety)
            elif move_flag==1:                          
                print("move_flag:",move_flag)
                testdef.sendMessage(ser,57)
                time.sleep(0.01)
                break
        move_flag=0
        # line_flag=0
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
            detx1,dety1,move_flag=testdef.circlePut1(cap)
            testdef.sendMessage2(ser,detx1,dety1)
            if move_flag==1:                          
                print("move_flag:",move_flag)
                testdef.sendMessage(ser,23)
                time.sleep(0.01)
                testdef.sendMessage(ser,24)
                move_flag=0
                break

    elif recv==b'st':
        pass

    elif recv==b'end':
        break


    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# code_cap.release()
cap.release()
cv2.destroyAllWindows()

