import cv2

def draw_dimensions(frame, interval=20):
    """
    ��ͼ����ÿ��һ�������ע���Ⱥ͸߶ȵ���ֵ��
    :param frame: ����ͼ��
    :param interval: ��ע�ļ�������أ�
    """
    height, width = frame.shape[:2]

    # # ��ע����
    # for x in range(interval, width, interval):
    #     cv2.putText(frame, f"{x}", (x, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # # ��ע�߶�
    # for y in range(interval, height, interval):
    #     cv2.putText(frame, f"{y}", (5, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    for y in range(interval, height, interval):
        cv2.line(frame, (0, y), (width, y), (0, 255, 0), 1)  # ��ɫ��
        cv2.putText(frame, f"{y}", (5, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # ���ƴ�ֱ������
    for x in range(interval, width, interval):
        cv2.line(frame, (x, 0), (x, height), (0, 255, 0), 1)  # ��ɫ��
        cv2.putText(frame, f"{x}", (x, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame

# ��ʼ������ͷ
cap = cv2.VideoCapture("/dev/up_video1",cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(3, 640)
cap.set(4, 480)
cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)

if not cap.isOpened():
    print("�޷�������ͷ")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("�޷���ȡ֡")
        break

    # ��ͼ���ϻ��Ƴߴ��ע
    annotated_frame = draw_dimensions(frame, interval=20)

    # ��ʾͼ��
    cv2.imshow("Annotated Frame", annotated_frame)

    # ���� 'q' ���˳�
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# �ͷ���Դ
cap.release()
cv2.destroyAllWindows()