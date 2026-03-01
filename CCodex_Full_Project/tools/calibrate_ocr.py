import argparse
import json

import cv2

from capture.capture_backend import MSSCapture
from capture.window_finder import find_window_by_title_substring, get_client_rect_screen
from core.telemetry import crop
from vision.ocr import _preprocess_digits
from vision.ocr_text import preprocess_text_roi


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--layout", default="config/layout.json")
    p.add_argument("--roi", required=True)
    p.add_argument("--mode", choices=["digits", "text"], default="text")
    return p.parse_args()


def main():
    args = parse_args()
    layout = json.loads(open(args.layout, encoding="utf-8").read())
    roi = layout.get("rois", {}).get(args.roi)
    if not roi:
        raise RuntimeError(f"ROI nicht gefunden: {args.roi}")

    wins = find_window_by_title_substring(layout["window_title_contains"])
    if not wins:
        raise RuntimeError("Fenster nicht gefunden")
    hwnd, _ = wins[0]
    cap = MSSCapture()

    while True:
        x, y, w, h = get_client_rect_screen(hwnd)
        frame = cap.grab_region(x, y, w, h)
        roi_img = crop(frame, roi)

        if args.mode == "digits":
            gray, th = _preprocess_digits(roi_img)
            cv2.imshow("gray", gray)
            cv2.imshow("threshold", th)
        else:
            dbg = preprocess_text_roi(roi_img)
            cv2.imshow("gray", dbg["gray"])
            cv2.imshow("scaled", dbg["scaled"])
            cv2.imshow("threshold", dbg["threshold"])

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
