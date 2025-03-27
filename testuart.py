#####测试串口通信

import cv2
import numpy as np
import serial 
import math
import time
import testdef

ser  =  serial.Serial( port="/dev/ttyAMA2",
                              baudrate=115200,
                              bytesize=serial.EIGHTBITS,
                              parity=serial.PARITY_NONE,
                              stopbits=serial.STOPBITS_ONE,
                              )   



data_l=0
# while True:
    # # data1=423
    # # data2=297
    # data_l+=1
    # # data_x=0
    # # data_y=0
    # # # testdef.sendMessage2(ser,data1,data2)
    # # testdef.sendMessage5(ser,data_l,data_x,data_y)
    # testdef.sendMessage(ser,data_l)
    # recv=testdef.receiveMessage(ser)
    # print(f"Received message: {recv}")
    # # testdef.sendMessage(ser,39)
    # time.sleep(0.01)
while True:
    
    data=None
    flag=1
    while flag:
        recv=testdef.receiveMessage(ser)
        print(recv)
        if recv is not None:
            data=recv
            flag=0
    # data=b'123+321'
    print("original:",len(data))
    data=data.decode("utf8")
    print(data,len(data))
    data1 = data[0:3]
    data2 = data[4:7]
    print("data1",data1)
    print("data2",data2)
    get_order=testdef.sort(data1)
    put_order=testdef.sort(data2)
    print(get_order,put_order)
