
import re
import cv2
import pytesseract

# If needed:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

_DIGITS = re.compile(r"\d+")

def ocr_digits(bgr):
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(th, config="--psm 7 -c tessedit_char_whitelist=0123456789")
    m = _DIGITS.search(text)
    return int(m.group()) if m else None
