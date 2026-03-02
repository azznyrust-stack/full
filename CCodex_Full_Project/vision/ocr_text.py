import cv2

from vision.easyocr_engine import get_easyocr_reader


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
    reader = get_easyocr_reader()
    chunks = reader.readtext(dbg["threshold"], detail=0, paragraph=False)
    normalized = "\n".join(chunk.strip() for chunk in chunks if chunk.strip())
    dbg["text"] = normalized
    return normalized, dbg
