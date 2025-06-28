import cv2
import numpy as np
import math
import time
import serial 
import testdef


class FunctionHandler:
    def __init__(self):
        # 硬件资源初始化
        self.cap = None
        self.code_cap = None
        self.ser = testdef.serialInit()
        self.frame_width = 1280
        self.frame_height = 720
        # 全局状态变量
        # 二维码信息
        self.get_order = [2,3,1]
        self.put_order = [1,3,2]
        # 标志位
        # self.line_flag = 0
        # self.move_flag = 0
        self.move_flag_color=0
        self.move_flag_color_1=0
        self.move_flag_color_2=0
        # 轮次计数（后续取消，放到32里计数
        self.circle_time = 1
        self.plate_time = 1
        self.recv = ''
        # 不记得是啥
        self.get_order_blank=[]

    # # 默认初始值，后续改掉
    # get_order=[2,3,1]
    # put_order=[1,3,2]

    def init_camera_up(self):
        """初始化上部摄像头"""
        self.cap = cv2.VideoCapture("/dev/up_video1", cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.cap.set(3, self.frame_width)
        self.cap.set(4, self.frame_height)
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 10)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def init_camera_code(self):
        """初始化二维码摄像头"""
        self.code_cap = cv2.VideoCapture("/dev/code_video1", cv2.CAP_V4L2)
        self.code_cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.code_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.code_cap.set(cv2.CAP_PROP_BRIGHTNESS, 10)
        self.code_cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
    
    def check_camera(self, cap_check, cam_name="摄像头"):
        """检查摄像头状态"""
        if not hasattr(self, 'cap') or cap_check is None:
            print(f"{cam_name}未初始化")
            return False
            
        check_ok = cap_check.isOpened()
        print(f"{cam_name}状态: {'正常' if check_ok else '异常'}")
        return check_ok

    def get_code(self):
        """处理二维码识别"""
        if not self.check_camera(self.code_cap,"二维码摄像头"):
            self.init_camera_code()
        time_c = time.time()
        time_code = 15
        code_end = 0
        data = ""
        while (time.time() - time_c < time_code) and (not code_end):
            data, code_flag = testdef.code(self.code_cap)
            if len(data) == 7 and code_flag == 1:
                code_end = 1
                break
        self.get_order = testdef.sort(data[0:3])
        self.put_order = testdef.sort(data[4:7])
        order = self.get_order + self.put_order
        testdef.sendMessage3(self.ser,order)
        time.sleep(0.002)
        testdef.sendMessage3(self.ser,order)
        time.sleep(0.002)
        testdef.sendMessage3(self.ser,order)
        self.code_cap.release()
        self.code_cap = None
        self.recv = b'st'

    def get_from_plate(self, plate_order):
        """处理转盘夹取物料"""
        if not self.check_camera(self.cap,"上部摄像头"):
            self.init_camera_up()
        stop_flag=0   #初始化转盘是否停止标志位
        i = 0   #运行轮数
        while i < 3:
        ####依据颜色顺序循环处理3个物料
            # print("iii:",i)
            # flagno = testdef.detectPlate(cap, 1)
            ret=self.cap.grab()
            while not stop_flag:
                print("i:",i)
                flag2 = testdef.detectPlate(self.cap,plate_order[i])
                x_,y_,img_,flag1,detx,dety = testdef.findBlockCenter(self.cap,plate_order[i])
                ####当所看对应颜色物料静止时
                if  (flag2 == 1 and flag1 == 1):
                    stop_flag = plate_order[i]  #令标志位为颜色序号
                    print("stop_flag",stop_flag)
                    testdef.sendMessage2(self.ser,detx,dety)  #给机械臂发送大致调整参数，机械臂只动一下
                    time.sleep(0.01)
                    if stop_flag == 1:  #发送到位信息，不同颜色发送不同值
                        testdef.sendMessage(self.ser,7)
                    elif stop_flag == 2:
                        testdef.sendMessage(self.ser,8)
                    elif stop_flag == 3:
                        testdef.sendMessage(self.ser,9)
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
                flag_check=testdef.detectPlate_check(self.cap,plate_order[i])
                # Time2=time.time()-Time
                # print("Time2:",Time2)
                print("flag_chexk:",flag_check)
                if flag_check :  #如果夹到了继续下一个颜色
                    print("next colorrrrrrrrrrrrrrrrrrrr")
                    i=i+1
                else:  #没夹到仍等待第一个,机械臂不回头放物料，直接下降
                    testdef.sendMessage(self.ser,3)
            else :
                time.sleep(3)
                i=i+1
            # time.sleep(3)
            # i=i+1
            ret=self.cap.grab()
            ret=self.cap.grab()
        cv2.destroyAllWindows()
        self.recv=b'st'


    # 粗定位函数：直线和圆环一起调整
    def cu_positioning(self, limit_circle=4, limit_line=0.5, timeout_cu=5):
        """粗定位车身位置（直线和圆环一起调整）"""
        ret=self.cap.grab()
        print("cccccccccccc")
        line_flag=0   #粗调时的直线圆环标志位置0
        move_flag=0
        while not self.cap.isOpened():
            print("Not open colorcap")
        # for i in range(2):
        #     q=cap.grab()
        ####粗调 圆环粗定位和直线一起调整
        ####粗调开始计时
        Time1=time.time()   
        # time_together=5   #粗调超时
        ####发送偏差值信息，调整车身位置直到超时或者直线圆环均到位
        while ((time.time()-Time1)<timeout_cu) and ((not line_flag) or (not move_flag)) :
            theta,line_flag,detx,dety,move_flag=testdef.together_line_circle1(self.cap,limit_position_circle=limit_circle, 
                                                                              limit_position_line=limit_line)
            if line_flag==0 or move_flag==0:
                if line_flag ==1:   #直线到位则后续角度一直为0
                    theta=0
                if move_flag ==1:   #圆环到位则后续xy一直为0
                    detx=0
                    dety=0
                testdef.sendMessage5(self.ser,theta,detx,dety)
        print("together okokokokokokokokok line_flag:",line_flag,"move_flag:",move_flag)
        testdef.sendMessage(self.ser,68)  #发送到位信息
        time.sleep(0.001)
        move_flag=0  #标志位清零以便下次使用
        line_flag=0
        ret=self.cap.grab()
        cv2.destroyAllWindows()

    # 细调函数：颜色定位和灰度定位
    def xi_positioning(self, circle_order, timeout_xi=2):
        """细调圆环位置（颜色定位和灰度定位）"""
        for i in range(3):
            ret=self.cap.grab()
            testdef.g_prev_smoothed_circle=None
            print("iiiiiiiiiiiiii:",i,"color:",circle_order[i])
            ####接收到爪子下降消息再开始进入细调
            recv_first=None
            while True:
                recv_first=testdef.receiveMessage(self.ser)
                if recv_first==b'near ground':
                    print("recv_first",recv_first)
                    break
            ####细调开始计时
            # for j in range(3):
            #     q=cap.grab()
            Time3=time.time()
            ####细调第一步 颜色定五环
            move_flag_color_1=0 
            while (not move_flag_color_1 and (time.time()-Time3)<timeout_xi):
            # while (not move_flag_color_1):
            # while((time.time()-Time3)<timeout_xi):
                timee=time.time()
                print("cccccccccccc")
                # q=cap.grab()
                x_,y_,img_,move_flag_color_1,detx_p,dety_p = testdef.circlePut_color(self.cap,circle_order[i])
                if move_flag_color_1==0:    #flag=1后那次数据不需发送
                    testdef.sendMessage2(self.ser,detx_p,dety_p)
                    print("cutiao time:",time.time()-timee)
            print("xitiao11 okokokokokokokokok")
            move_flag_color_1=0   
            #细调第二步 灰度定中心（第一版-无到位后二次检测
            move_flag_color_2=0
            while (not move_flag_color_2 and (time.time()-Time3)<timeout_xi):
            # while (not move_flag_color_2 ):
                print("xxxxxxxx")
                timeee=time.time()
                detx,dety,move_flag_color_2=testdef.circlePut1(self.cap)
                if move_flag_color_2==0:
                    testdef.sendMessage2(self.ser,detx,dety)
                    print("xitiao time:",time.time()-timeee)
            # ###细调第二步 灰度定中心（第二版-到位后做二次检测-防止物料贴环边立即就放
            # move_flag_color_2_2=0
            # while (not move_flag_color_2_2 and (time.time()-Time3)<timeout_xi):
            # # while (not move_flag_color_2_2 ):
            #     print("xxxxxxxx")
            #     timeee=time.time()
            #     detx,dety,move_flag_color_2=testdef.circlePut1(self.cap)
            #     # timeuart=time.time()
            #     # print("xitiao time:",time.time()-timeee)
            #     # testdef.sendMessage2(ser,detx,dety)
            #     # print("xitiao time:",time.time()-timeuart)
            #     if move_flag_color_2==0:
            #         # a=1
            #         testdef.sendMessage2(self.ser,detx,dety)
            #         print("xitiao time:",time.time()-timeee)
            #     else:
            #         # detxx=0
            #         # detyy=0
            #         flagg=0
            #         time_check=2
            #         ####初次到位后再看一次是否还在中心内 若在则到位 若不在则继续调整
            #         for k in range(time_check):
            #             detx2,dety2,move_flag_color_22=testdef.circlePut1(self.cap)
            #             testdef.sendMessage2(self.ser,detx2,dety2)
            #             # print("double check")
            #             # detxx+=detx
            #             # detyy+=dety
            #             flagg+=move_flag_color_22
            #             print("double check    flagg:",flagg)
            #         if flagg==time_check:
            #             move_flag_color_2_2=1
            #             break
            #         move_flag_color_2_2=1
            #         break
            print("xitiao22 okokokokokokokokok  move_flag_color_2:",move_flag_color_2)
            ####发送到位信息 根据颜色发送不同到位信息
            if circle_order[i] == 1:
                testdef.sendMessage(self.ser,57)
            elif circle_order[i] == 2:
                testdef.sendMessage(self.ser,64)
            elif circle_order[i] == 3:
                testdef.sendMessage(self.ser,65)
            time.sleep(0.01)
            move_flag_color_2=0
            # i = i+1  #继续下一个颜色
            cv2.destroyAllWindows()
        ret=self.cap.grab()
        self.recv=b'st'  #完成功能后进入空循环

    def adjust_line_gray_yellow(self,timeout_line=5):
        """调整直线——灰黄交界"""
        while not self.cap.isOpened():
            print("Not open colorcap")
        ####开始计时
        line_flag=0
        ret=self.cap.grab()
        Time_l=time.time()
        ####调整车身姿态直到直线到位或超时
        while (not line_flag and (time.time()-Time_l)<timeout_line):
        # while (not line_flag):
            ####清理视频流缓存区
            # for i in range(4):
            #     # theta1,line_flag1=testdef.detectLine(cap)
            #     ret=cap.grab()
            theta,line_flag=testdef.detectLine_gray(self.cap)
            # theta,line_flag=testdef.detectLine(cap)
            if line_flag ==0:   #到位后当次偏差值不发送
                testdef.sendMessage5(self.ser,theta,0,0)
                print("main li de theta:",theta)
            # elif line_flag==1:
        print("line_flag:",line_flag)
        testdef.sendMessage(self.ser,39)
        time.sleep(0.003)
        testdef.sendMessage(self.ser,40)
        time.sleep(0.003)
        testdef.sendMessage(self.ser,68)
        line_flag=0
        ret=self.cap.grab()
        ret=self.cap.grab()

    def cu_positioning_test(self,timeout_cu=5):
        '''测试代码：粗调先调直线再调xy方向'''
        ret=self.cap.grab()
        print("cccccccccccc")
        line_flag=0   #粗调时的直线圆环标志位置0
        move_flag=0
        while not self.cap.isOpened():
            print("Not open colorcap")
        # for i in range(2):
        #     q=cap.grab()
        ####粗调 圆环粗定位和直线一起调整
        ####粗调开始计时
        Time1=time.time()   
        ####发送偏差值信息，调整车身位置直到超时或者直线圆环均到位
        while ((time.time()-Time1)<timeout_cu) and ((not line_flag) or (not move_flag)) :
            theta,line_flag,detx,dety,move_flag=testdef.together_line_circle1(self.cap)
            if line_flag==0:
                detx=0
                dety=0
            elif line_flag ==1:   #直线到位则后续角度一直为0
                theta=0
            testdef.sendMessage5(self.ser,theta,detx,dety)
        print("together okokokokokokokokok line_flag:",line_flag,"move_flag:",move_flag)
        testdef.sendMessage(self.ser,68)  #发送到位信息
        time.sleep(0.001)
        move_flag=0  #标志位清零以便下次使用
        line_flag=0
        ret=self.cap.grab()
        cv2.destroyAllWindows()


    



    def reset_state(self):
        print("endendendendnendnendnendne")
        cv2.destroyAllWindows()
        ####初始化侧边二维码摄像头
        self.init_camera_code()  # 初始化摄像头
        if  not self.code_cap.isOpened():
            print("faillllllllll")
        ####初始化各个变量
        self.get_order=[]
        self.put_order=[]


    
    





