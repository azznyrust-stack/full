
import numpy as np
import mss

class MSSCapture:
    def __init__(self):
        self.sct = mss.mss()

    def grab_region(self, x, y, w, h):
        mon = {"left": int(x), "top": int(y), "width": int(w), "height": int(h)}
        img = np.array(self.sct.grab(mon))
        return img[:, :, :3].copy()
