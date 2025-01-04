import cv2
import numpy as np
# import uvc


# #��������ͷ��������
capture_width = 640   #
capture_height = 480
framerate = 60			# ֡��
#չʾͼƬ��С
display_width = 640
display_height = 480
flip_method = 0			# ����
npzfile = np.load('calibrate.npz')
mtx = npzfile['mtx']
dist = npzfile['dist']
def undistortion(img, mtx, dist):   #jibian 
    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

    # print('roi ', roi)

    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

    # crop the image
    x, y, w, h = roi
    if roi != (0, 0, 0, 0):
        dst = dst[y:y + h, x:x + w]

    return dst

# def gstreamer_pipeline(
#     capture_width=1920,  # ����ͷԤ�����ͼ�����
#     capture_height=1080,  # ����ͷԤ�����ͼ��߶�
#     framerate=60,         # ����֡��
# ):
#     return (
#         "v4l2src device=/dev/video0 ! "
#         "video/x-raw, "
#         "width=(int)%d, height=(int)%d, "
#         "format=(string)I420, framerate=(fraction)%d/1 ! "
#         "videoconvert ! "
#         "video/x-raw, format=(string)BGR ! "
#         "appsink"
#         % (
#             capture_width,
#             capture_height,
#             framerate,
#         )
#     )
    
# color_cap = cv2.VideoCapture(gstreamer_pipeline(capture_width,
#                                         capture_height,
#                                         framerate,),
#                     cv2.CAP_GSTREAMER)
# color_cap.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc(M','J','P','G'))

# if not color_cap.isOpened():
#     print("cant open")
#     exit()

cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
# cap = cv2.VideoCapture("/dev/code_video",cv2.CAP_V4L2)
# cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('Y', 'U', 'Y', 'V'))
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
# cap.set(3, 640)#��
# cap.set(4, 480)#��
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
cap.set(cv2.CAP_PROP_EXPOSURE, float(0.6)) 


# cap1 = cv2.VideoCapture("/dev/video2",cv2.CAP_V4L2)
# # cap = cv2.VideoCapture("/dev/video2")
# # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
# cap1.set(3, 640)#��
# cap1.set(4, 480)#��

while True:
    success, img = cap.read()
    print(success)
    corrected_frame=undistortion(img,mtx,dist)
    # success1, img1 = cap1.read()
    # print(success)
    cv2.imshow("Original",corrected_frame)
    # cv2.imshow("Original1",img1)

    cv2.waitKey(1)    

cap.release()
cv2.destroyAllWindows()
