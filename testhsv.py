import cv2
import numpy as np

def empty():
    pass




# cap = cv2.VideoCapture(2,cv2.CAP_V4L2)
cap = cv2.VideoCapture("/dev/up_video1",cv2.CAP_V4L2)
# cap = cv2.VideoCapture("/dev/code_video1",cv2.CAP_V4L2)
# cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(3, 1280)#��
cap.set(4, 720)#��
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
# cap.set(cv2.CAP_PROP_EXPOSURE, float(0.6)) 
cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
# ret = cap.grab()

# #初始置0数字
# hmin=0
# hmax=179
# smin=0
# smax=255
# vmin=0
# vmax=255

# #红色1
# hmin=0
# hmax=12
# smin=60
# smax=203
# vmin=60
# vmax=255

# #红色2
# hmin=160
# hmax=180
# smin=50
# smax=255
# vmin=50
# vmax=255

#绿色（能看浅色圆环
hmin=32
hmax=78
smin=48
smax=234
vmin=54
vmax=255

# #绿色（避免看到黄色
# hmin=40
# hmax=78
# smin=48
# smax=234
# vmin=54
# vmax=255

# #蓝色
# hmin=82
# hmax=120
# smin=70
# smax=255
# vmin=0
# vmax=255

cv2.namedWindow("TrackBars")
cv2.resizeWindow("TrackBars",640,240)
cv2.createTrackbar("Hue Min","TrackBars",hmin,179,empty)
cv2.createTrackbar("Hue Max","TrackBars",hmax,179,empty)
cv2.createTrackbar("Sat Min","TrackBars",smin,255,empty)
cv2.createTrackbar("Sat Max","TrackBars",smax,255,empty)
cv2.createTrackbar("Val Min","TrackBars",vmin,255,empty)
cv2.createTrackbar("Val Max","TrackBars",vmax,255,empty)

while True:
    success, img = cap.read()
    imgHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    h_min = cv2.getTrackbarPos("Hue Min","TrackBars")
    h_max = cv2.getTrackbarPos("Hue Max", "TrackBars")
    s_min = cv2.getTrackbarPos("Sat Min", "TrackBars")
    s_max = cv2.getTrackbarPos("Sat Max", "TrackBars")
    v_min = cv2.getTrackbarPos("Val Min", "TrackBars")
    v_max = cv2.getTrackbarPos("Val Max", "TrackBars")
    # print(h_min,h_max,s_min,s_max,v_min,v_max)
    lower = np.array([h_min,s_min,v_min])
    upper = np.array([h_max,s_max,v_max])
    mask = cv2.inRange(imgHSV,lower,upper)
    imgResult = cv2.bitwise_and(img,img,mask=mask)


    cv2.imshow("Original",img)
    # cv2.imshow("HSV",imgHSV)
    cv2.imshow("Mask", mask)
    cv2.imshow("Result", imgResult)

    # imgStack = stackImages(0.6,([img,imgHSV],[mask,imgResult]))
    # cv2.imshow("Stacked Images", imgStack)

    cv2.waitKey(1)
