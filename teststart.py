#Raspberry Pi self starting

import cv2
import serial
import testdef
import time

ser=testdef.serialInit()
recv=''
while True:

    recv_mess = testdef.receiveMessage(ser)
    if recv_mess != None:
        print("recv_mess:",recv_mess)
    if recv_mess != None:
        if recv_mess == b'ZZ' or recv_mess==b'BB' or recv_mess==b'CC' or recv_mess==b'DD' or recv_mess==b'EE' or recv_mess==b'FF' or recv_mess==b'GG' or recv_mess==b'st':
            recv=recv_mess
    # print("first  recv:",recv)
    print(recv)

    if recv==b'ZZ':
        testdef.sendMessage(ser,136)
        time.sleep(0.01)

    cv2.waitKey(1)   