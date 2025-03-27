import cv2
import numpy as np

# ȫ�ֱ��������ڴ洢���ѡ�����������ͱ�־λ
selected_rect = None
selecting = False

def on_mouse(event, x, y, flags, param):
    global selected_rect, selecting
    if event == cv2.EVENT_LBUTTONDOWN:
        selected_rect = (x, y, 0, 0)
        selecting = True
    elif event == cv2.EVENT_LBUTTONUP:
        selected_rect = (selected_rect[0], selected_rect[1], x - selected_rect[0], y - selected_rect[1])
        selecting = False

def main():
    global selected_rect
    frameWidth = 1280
    frameHeight = 720
    # ������ͷ
    cap = cv2.VideoCapture("/dev/up_video1",cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    cap.set(3, frameWidth)
    cap.set(4, frameHeight)
    cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)

    cv2.namedWindow("Real-time Video")
    cv2.setMouseCallback("Real-time Video", on_mouse)

    # ѭ��ֱ���ɹ�ѡ������
    while True:
        # ��ȡһ֡
        ret, frame = cap.read()
        if not ret:
            break
        if selecting and selected_rect is not None:
            # ����Ƶ֡�ϻ������ѡ��ľ��ο�
            x, y, w, h = selected_rect
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        # ��ʾʵʱ��Ƶ
        cv2.imshow("Real-time Video", frame)
        # ���ѡ�������������һ������ѡ����Ĵ���
        if not selecting and selected_rect is not None and selected_rect[2] > 0 and selected_rect[3] > 0:
            hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # ��RGBת��HSV
            x, y, w, h = selected_rect
            imagePart = hsvImage[y:y+h, x:x+w]
            channels = imagePart.shape[-1]
            if channels == 3:
                hValues = imagePart[:, :, 0].mean()  # Hͨ��ƽ��ֵ
                sValues = imagePart[:, :, 1].mean()  # Sͨ��ƽ��ֵ
                vValues = imagePart[:, :, 2].mean()  # Vͨ��ƽ��ֵ

                if not (hValues != hValues or sValues != sValues or vValues != vValues):
                    print("Mean H value:", hValues)
                    print("Mean S value:", sValues)
                    print("Mean V value:", vValues)

                    # ʹ������HSV��ֵ������ֵ�˲�
                    lower_bound = (int(hValues - 10), int(sValues - 50), int(vValues - 60))
                    upper_bound = (int(hValues + 10), int(sValues + 50), int(vValues + 30))
                    print("lower_bound",lower_bound,"upper_bound",upper_bound)

                    # ѭ���������̶�ʹ������HSV��ֵ������ԭʼͼ������˲�
                    break

        # ����'q'���˳�ѭ��
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # ������������ԭʼͼ�񲢽����˲�
    while True:
        # ��ȡһ֡
        ret, frame = cap.read()
        if not ret:
            break
        # �����˲�����
        hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # ��RGBת��HSV
        filteredImage = cv2.inRange(hsvImage, lower_bound, upper_bound)
        # ��ʾ�˲����ͼ��
        cv2.imshow("Filtered Image", filteredImage)
        # ��ʾʵʱ��Ƶ
        cv2.imshow("Real-time Video", frame)
        # ����'q'���˳�ѭ��
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # �ͷ�����ͷ��Դ
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()