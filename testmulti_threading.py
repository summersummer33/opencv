import cv2
import threading




#multi_threading
class VideoCaptureThread:
    def __init__(self, index=0):
        self.cap = cv2.VideoCapture("/dev/up_video",cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS,10)
        # self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.frame = None
        self.running = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.update)
        self.thread.start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:  # ȷ���̰߳�ȫ
                    self.frame = frame

    def read(self):
        with self.lock:  # ȷ���̰߳�ȫ
            return self.frame

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()


# ʹ��ʾ��
# video_capture = VideoCaptureThread()
cap = VideoCaptureThread()

while True:
    frame = cap.read()
    if frame is not None:
        cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.stop()
cv2.destroyAllWindows()
