import re
from collections import deque
from statistics import median

import cv2
import pytesseract

_DIGITS = re.compile(r"\d+")


class DigitSmoother:
    def __init__(self, window=5, max_jump=5_000_000):
        self.window = max(1, int(window))
        self.max_jump = max_jump
        self.values = deque(maxlen=self.window)
        self.last_stable = None

    def update(self, value):
        if value is None:
            return self.last_stable

        if self.last_stable is not None and abs(value - self.last_stable) > self.max_jump:
            return self.last_stable

        self.values.append(value)
        stable = int(median(self.values))
        self.last_stable = stable
        return stable


def _preprocess_digits(bgr):
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return gray, th


def ocr_digits(bgr, return_debug=False):
    gray, th = _preprocess_digits(bgr)
    text = pytesseract.image_to_string(th, config="--psm 7 -c tessedit_char_whitelist=0123456789")
    m = _DIGITS.search(text)
    value = int(m.group()) if m else None
    if return_debug:
        return value, {"gray": gray, "threshold": th, "raw_text": text.strip()}
    return value
