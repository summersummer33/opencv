import cv2
import numpy as np
import math
import time
import serial 
import testdef
import threading
import testfcn  # 导入封装好的功能处理器

# 初始化处理器
handler = testfcn.FunctionHandler()
handler.init_camera_code()  # 初始化摄像头
handler.init_camera_up()  # 初始化摄像头
recv=''

while True:
    # 接收串口消息
    recv_mess = testdef.receiveMessage(handler.ser)
    if recv_mess != None:
        print("recv_mess:",recv_mess)
    if recv_mess != None:
        #### 根据接收到的指令更新recv
        # if (recv_mess == b'AA' or recv_mess==b'BB' or recv_mess==b'CC' or recv_mess==b'DD' or recv_mess==b'EE' 
        #     or recv_mess==b'FF' or recv_mess==b'GG' or recv_mess==b'HH' or recv_mess==b'LL' or recv_mess==b'st'):
        if recv_mess in [b'AA', b'BB1', b'BB2', b'CC12', b'CC3', b'CC4',  b'EE', 
                         b'FF', b'GG', b'HH', b'II', b'JJ', b'KK', b'LL', b'MM', b'NN', b'OO', b'PP', b'QQ',
                         b'st', b'end',
                         b'DD']:
            recv=recv_mess


    #############################################################################################
    ########################初赛正常流程使用代码（轻易不要改动！！！）###############################
    #############################################################################################

####识别二维码、条形码
    if recv == b'AA':
        handler.get_code()
        recv = b'st'

####识别转盘 夹取物料（正常流程
    #第一顺序
    elif recv == b'BB1':
        handler.get_from_plate(handler.get_order)
        recv = b'st'

    #第二顺序
    elif recv == b'BB2':
        handler.get_from_plate(handler.put_order)
        recv = b'st'

####识别圆环 放置物料
    #粗调+第一顺序
    elif recv == b'CC12':
        handler.cu_positioning()
        handler.xi_positioning(handler.get_order)
        recv = b'st'

    #粗调+第二顺序
    elif recv == b'CC3':
        handler.cu_positioning()
        handler.xi_positioning(handler.put_order)
        recv = b'st'

    #粗调
    elif recv == b'CC4':
        # handler.cu_positioning(50,100)
        handler.cu_positioning()
        recv = b'st'

####识别直线 在转盘旁调整车身
    elif recv == b'EE':
        handler.adjust_line_gray_yellow()
        recv = b'st'


############测试
    elif recv == b'QQ':
        handler.cu_positioning_test()
        recv = b'st'

    #############################################################################################
    ##############################决赛功能备用代码################################################
    #############################################################################################


    #############################################################################################
    ####################################模拟赛使用################################################
    #############################################################################################



    #############################################################################################
    #################################空循环及清零部分#############################################
    #############################################################################################

####待机状态
    elif recv == b'st':
        pass

####全局标志位清零 可直接开始第二轮
    elif recv == b'end':
        handler.reset_state()  # 复位状态


    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# 退出时清理资源
handler.cleanup()

