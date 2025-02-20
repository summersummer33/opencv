import cv2
import numpy as np
import serial 
import math
import time

ser  =  serial.Serial( port="/dev/ttyAMA2",
                              baudrate=115200,
                              bytesize=serial.EIGHTBITS,
                              parity=serial.PARITY_NONE,
                              stopbits=serial.STOPBITS_ONE,
                              )   




while True:
    data1=10
    data2=10
    data_l=15
    data_x=17
    data_y=16

    # if data1>0:
    #     signal1=1
    # else :
    #     signal1=2
    #     data1=abs(data1)
    # if data2>0:
    #     signal2=1
    # else:
    #     signal2=2
    #     data2=abs(data2)
    # data_hex1=hex(data1)[2:]
    # data_hex1 = data_hex1.zfill(2)
    # data_hex2=hex(data2)[2:]
    # data_hex2 = data_hex2.zfill(2)
    # signal_hex1=hex(signal1)[2:]
    # signal_hex1 = signal_hex1.zfill(2)
    # signal_hex2=hex(signal2)[2:]
    # signal_hex2 = signal_hex2.zfill(2)
    # # print(data_hex)
    # # data_pack = data_hex1+data_hex2
    # data_pack = signal_hex1+data_hex1+signal_hex2+data_hex2
    # # data_pack =data_hex
    # # ser.write(bytes.fromhex(data))
    # ser.write(bytes.fromhex(data_pack))
    # # ser.write(bytes.fromhex(data_hex1))
    # # ser.write(bytes.fromhex(data_hex1))
    # print(data_pack)
    # time.sleep(0.1)


    # signal1=1 if data1>=0 else 2
    # data1=min(abs(data1),254)
    # signal2=1 if data2>=0 else 2
    # data2=min(abs(data2),254)

    # data_hex1=f"{data1:02X}"
    # data_hex2=f"{data2:02X}"
    # signal_hex1=f"{signal1:02X}"
    # signal_hex2=f"{signal2:02X}"

    # data_pack = signal_hex1+data_hex1+signal_hex2+data_hex2
    # ser.write(bytes.fromhex(data_pack))
    # print(data_pack)
    # time.sleep(0.1)

    signal_l = 1 if data_l >= 0 else 2
    signal_x = 1 if data_x >= 0 else 2
    data_x = min(abs(data_x), 254)
    signal_y = 1 if data_y >= 0 else 2
    data_y = min(abs(data_y), 254)
    data_pack = (
        f"{signal_l:02X}{data_l:02X}"  # data_l
        f"{signal_x:02X}{data_x:02X}"  # data_x
        f"{signal_y:02X}{data_y:02X}"  # data_y
    )
    ser.write(bytes.fromhex(data_pack))
    print("together:", data_pack)
    time.sleep(0.1)