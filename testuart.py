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
    if data1>0:
        signal1=1
    else :
        signal1=2
        data1=abs(data1)
    if data2>0:
        signal2=1
    else:
        signal2=2
        data2=abs(data2)
    data_hex1=hex(data1)[2:]
    data_hex1 = data_hex1.zfill(2)
    data_hex2=hex(data2)[2:]
    data_hex2 = data_hex2.zfill(2)
    signal_hex1=hex(signal1)[2:]
    signal_hex1 = signal_hex1.zfill(2)
    signal_hex2=hex(signal2)[2:]
    signal_hex2 = signal_hex2.zfill(2)
    # print(data_hex)
    # data_pack = data_hex1+data_hex2
    data_pack = signal_hex1+data_hex1+signal_hex2+data_hex2
    # data_pack =data_hex
    # ser.write(bytes.fromhex(data))
    ser.write(bytes.fromhex(data_pack))
    # ser.write(bytes.fromhex(data_hex1))
    # ser.write(bytes.fromhex(data_hex1))
    print(data_pack)
    time.sleep(0.1)