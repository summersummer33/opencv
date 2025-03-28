#HSV in histogram
#Display the values of the three channels of HSV using histograms

import cv2
import numpy as np
import time
import testdef
from matplotlib import pyplot as plt

framerate = 60			# ֡��


cap = cv2.VideoCapture("/dev/up_video1",cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
# ret = cap.grab()




def enhance_frame_hsv(frame):
    """
    �Ե�֡ͼ����� HSV �ռ��е�����Ӧ��ǿ��
    ��Ҫ��ǿ���ȺͶԱȶȣ�ͬʱ������ɫ��Ϣ��
    """
    # ��ͼ��� BGR ת��Ϊ HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # ������ͨ����V��Ӧ������Ӧֱ��ͼ���⻯��CLAHE��
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    v_enhanced = clahe.apply(v)

    # ����Ӧ�������Ͷȣ�S��ͨ��
    s_enhanced = np.clip(s * 1.5, 0, 255).astype(np.uint8)

    # �ϲ���ǿ��� HSV ͨ��
    hsv_enhanced = cv2.merge([h, s_enhanced, v_enhanced])

    # ����ǿ��� HSV ͼ��ת���� BGR
    enhanced_frame = cv2.cvtColor(hsv_enhanced, cv2.COLOR_HSV2BGR)
    return enhanced_frame



while True:
    # Time1=time.time()
    success, img = cap.read()


    enhanced_frame = enhance_frame_hsv(img)

    # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2HSV)
    
    # ��ȡHSV�е�Hͨ������
    # h = hsv[:, :, 0].ravel()
    
    # # ��ʾ����ͷ�Ļ���
    # cv2.imshow("Camera Frame", img)
    
    # # ����Hͨ��ֱ��ͼ
    # plt.hist(h, 180, [0, 180], color='r', alpha=0.7)
    # plt.title("Hue Histogram")
    # plt.xlabel("Hue Value")
    # plt.ylabel("Frequency")
    # plt.pause(0.01)  # ��ͣһ��ʱ���Ը���ֱ��ͼ
    # plt.clf()  # �����ǰֱ��ͼ��Ϊ��һ֡��׼��




    h = hsv[:, :, 0].ravel()  # ɫ��
    s = hsv[:, :, 1].ravel()  # ���Ͷ�
    v = hsv[:, :, 2].ravel()  # ����
    
    # ��ʾ����ͷ�Ļ���
    cv2.imshow("Camera Frame", enhanced_frame)
    
    # ����HSVͨ����ֱ��ͼ
    plt.clf()  # �����ǰͼ��
    plt.title("HSV Histogram")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    
    # ����Hͨ��ֱ��ͼ
    plt.subplot(3, 1, 1)  # 3��1�еĵ�1��
    plt.hist(h, 180, [0, 180], color='r', alpha=0.7)
    plt.title("Hue Histogram")
    
    # ����Sͨ��ֱ��ͼ
    plt.subplot(3, 1, 2)  # 3��1�еĵ�2��
    plt.hist(s, 256, [0, 256], color='g', alpha=0.7)
    plt.title("Saturation Histogram")
    
    # ����Vͨ��ֱ��ͼ
    plt.subplot(3, 1, 3)  # 3��1�еĵ�3��
    plt.hist(v, 256, [0, 256], color='b', alpha=0.7)
    plt.title("Value Histogram")

    plt.tight_layout()  # �Զ�������ͼ������ʹ֮�������ͼ������
    plt.pause(0.01)  # ��ͣһ��ʱ���Ը���ֱ��ͼ

    cv2.waitKey(1)   