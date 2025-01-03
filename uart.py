import cv2
import numpy as np
import serial 
import math
import time

ser  =  serial.Serial( port="/dev/ttyAMA2",
                              baudrate=9600,
                              bytesize=serial.EIGHTBITS,
                              parity=serial.PARITY_NONE,
                              stopbits=serial.STOPBITS_ONE,
                              )
if ser.isOpen == False:
    print("false")
    ser.open()
    # /dev/ttyAMA0

while True:
        # ��ý��ջ������ַ�
    ser.write(b'ok')
    # count = ser.inWaiting()
    # if count != 0:
    #         # ��ȡ���ݲ�����
    #     recv = ser.read(count)  #��ݮ�ɴ��ڽ�������
    #     ser.write(recv)         #��ݮ�ɴ��ڷ�������
    #     # ��ս��ջ�����
    # ser.flushInput()
        # ��Ҫ��������ʱ
    print(1)
    time.sleep(0.1)





# ����������16������ʽ
    