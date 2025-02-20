import cv2
import numpy as np
import time
# import uvc
import testdef


# #��������ͷ��������
# capture_width = 640   #
# capture_height = 480
framerate = 60			# ֡��
#չʾͼƬ��С
# display_width = 640
# display_height = 480
flip_method = 0			# ����
# npzfile = np.load('calibrate.npz')
# mtx = npzfile['mtx']
# dist = npzfile['dist']
# def undistortion(img, mtx, dist):   #jibian 
#     h, w = img.shape[:2]
#     newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

#     # print('roi ', roi)

#     dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

#     # crop the image
#     x, y, w, h = roi
#     if roi != (0, 0, 0, 0):
#         dst = dst[y:y + h, x:x + w]

#     return dst

#
# cap = cv2.VideoCapture(2,cv2.CAP_V4L2)
# cap = cv2.VideoCapture("/dev/up_video1",cv2.CAP_V4L2)
cap = cv2.VideoCapture("/dev/code_video1",cv2.CAP_V4L2)
# cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('Y', 'U', 'Y', 'V'))
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
# cap.set(3, 640)#��
# cap.set(4, 480)#��
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
# cap.set(cv2.CAP_PROP_EXPOSURE, float(0.6)) 
cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
# cap.set(cv2.CAP_PROP_EXPOSURE, float(0.1))
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
# ret = cap.grab()


while True:
    Time1=time.time()
    success, img = cap.read()
    print("time:",time.time()-Time1)
    # cv2.imshow("Original",img)



    src1 = img.copy()
    res1 = src1.copy()
    h, w = res1.shape[:2]
    print("h:",h,"w:,",w)
    detx,dety,move_flag_color_2=testdef.circlePut1(cap)

    cv2.waitKey(1)    

cap.release()
cv2.destroyAllWindows()







# import cv2
 
# #ѡ������ͷ�ţ�һ��� 0 ��ʼ
# # cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
# # cap.set(3, 352)#��
# # cap.set(4, 288)#��
# # cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
# # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3.0)
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1.0)
# cap.set(cv2.CAP_PROP_EXPOSURE, 166)
# # cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
# # cap.set(cv2.CAP_PROP_EXPOSURE, float(0.1)) 
# # cap.set(cv2.CAP_PROP_EXPOSURE, 100) 


 
# #�����ò�����Ȼ���ȡ����
# for i in range(47):
#     print("No.={} parameter={}".format(i,cap.get(i)))
 
# while True:
#     ret, img = cap.read()
#     cv2.imshow("input", img)
# # �� ESC ���˳�
#     key = cv2.waitKey(10)
#     if key == 27:
#         break
 
# cv2.destroyAllWindows() 
# cv2.VideoCapture(0).release()





# # import cv2

# # # ��ʼ������ͷ
# # cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
# # cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
# # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3.0)  # �ر��Զ��ع�
# # cap.set(cv2.CAP_PROP_EXPOSURE, 166)  # ��ʼ�ع�ֵ

# # # ��������
# # cv2.namedWindow("input")

# # # ����ص����������ڸ����ع�ֵ
# # def update_exposure(value):
# #     cap.set(cv2.CAP_PROP_EXPOSURE, value)

# # # ����������
# # cv2.createTrackbar("Exposure", "input", int(cap.get(cv2.CAP_PROP_EXPOSURE)), 10000, update_exposure)

# # # ��ʾ����ͷͼ��
# # while True:
# #     ret, img = cap.read()
# #     if not ret:
# #         print("�޷���ȡ����ͷͼ��")
# #         break

# #     cv2.imshow("input", img)

# #     # ���� ESC ���˳�
# #     key = cv2.waitKey(10)
# #     if key == 27:
# #         break

# # # �ͷ���Դ���رմ���
# # cap.release()
# # cv2.destroyAllWindows()