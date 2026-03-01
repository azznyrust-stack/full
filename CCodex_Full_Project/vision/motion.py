
import cv2
import numpy as np

class MotionDetector:
    def __init__(self):
        self.prev = None

    def score(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.prev is None:
            self.prev = gray
            return 0.0
        diff = cv2.absdiff(self.prev, gray)
        self.prev = gray
        return float(np.mean(diff) / 255.0)
