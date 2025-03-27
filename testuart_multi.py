
import cv2
import numpy as np
import serial
import math
import time
import testdef
import threading
import random

# 初始化串口
ser = serial.Serial(port="/dev/ttyAMA2",
                    baudrate=115200,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE)

# 全局变量
data_l = 0
data_x = 0
data_y = 0

# 接收消息的线程函数
def receive_message():
    while True:
        # 调用 testdef 模块中的 recvMessage 函数接收消息
        recv = testdef.receiveMessage(ser)
        if recv:
            print(f"Received message: {recv}")
        # 每10ms运行一次
        time.sleep(0.003)

# 发送消息的线程函数
def send_message():
    global data_l, data_x, data_y
    while True:
        data_l += 1
        # 模拟数据更新
        data_x = 0
        data_y = 0
        # 调用 testdef 模块中的 sendMessage5 函数发送消息
        testdef.sendMessage(ser, data_l)
        print(f"Sent message: data_l={data_l}")
        # 每260ms运行一次
        time.sleep(0.263)

# 创建线程
receive_thread = threading.Thread(target=receive_message)
send_thread = threading.Thread(target=send_message)

# 启动线程
receive_thread.start()
send_thread.start()

# 等待线程结束（虽然这里线程是无限循环的，不会结束）
receive_thread.join()
send_thread.join()