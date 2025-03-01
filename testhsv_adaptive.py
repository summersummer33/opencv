#adaptive histogram equalization

import cv2
import numpy as np

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

# ����Ƶ�ļ�������ͷ
# video_path = 'input_video.mp4'  # �滻Ϊ�����Ƶ·��������ʹ������ͷ��0
cap = cv2.VideoCapture("/dev/up_video1",cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# �����Ƶ�Ƿ�ɹ���
if not cap.isOpened():
    print("�޷�����Ƶ�ļ�������ͷ������·�����豸�Ƿ���ã�")
    exit()

# ��֡��ȡ��Ƶ
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("�޷���ȡ֡����Ƶ�����ѽ�����")
        break

    # ��ÿһ֡������ǿ����
    enhanced_frame = enhance_frame_hsv(frame)

    # ʵʱ��ʾ��ǿ���֡
    cv2.imshow('Original Frame', frame)  # ��ʾԭʼ֡����ѡ��
    cv2.imshow('Enhanced Frame', enhanced_frame)  # ��ʾ��ǿ���֡

    # ���� 'q' ���˳�ѭ��
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# �ͷ���Դ
cap.release()
cv2.destroyAllWindows()