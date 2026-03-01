import cv2
import pytesseract


def preprocess_text_roi(bgr):
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    scaled = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    blur = cv2.GaussianBlur(scaled, (3, 3), 0)
    th = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        6,
    )
    return {
        "gray": gray,
        "scaled": scaled,
        "threshold": th,
    }


def ocr_text_multiline(bgr):
    dbg = preprocess_text_roi(bgr)
    text = pytesseract.image_to_string(dbg["threshold"], config="--psm 6")
    normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    dbg["text"] = normalized
    return normalized, dbg
