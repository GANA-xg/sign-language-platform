import cv2

from config import CAMERA_ID

class Camera:

    def __init__(self):

        self.cap = cv2.VideoCapture(CAMERA_ID)

    def get_frame(self):

        success, frame = self.cap.read()

        return success, frame

    def release(self):

        self.cap.release()