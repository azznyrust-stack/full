
import json
import time
from pathlib import Path

from capture.window_finder import find_window_by_title_substring, get_client_rect_screen
from capture.capture_backend import MSSCapture
from vision.ocr import ocr_digits
from vision.motion import MotionDetector
from core.stats import FarmStats

def crop(frame, roi):
    h, w = frame.shape[:2]
    x = int(roi["x"] * w)
    y = int(roi["y"] * h)
    rw = int(roi["w"] * w)
    rh = int(roi["h"] * h)
    return frame[y:y+rh, x:x+rw]

def run():
    layout = json.loads(Path("config/layout.json").read_text())
    wins = find_window_by_title_substring(layout["window_title_contains"])
    if not wins:
        raise RuntimeError("Fenster nicht gefunden")
    hwnd, title = wins[0]
    print("Nutze Fenster:", title)

    cap = MSSCapture()
    motion = MotionDetector()
    stats = FarmStats()

    while True:
        x, y, w, h = get_client_rect_screen(hwnd)
        frame = cap.grab_region(x, y, w, h)

        gold = None
        if "gold_text" in layout["rois"]:
            gold = ocr_digits(crop(frame, layout["rois"]["gold_text"]))

        stats.update_gold(gold)
        motion_score = motion.score(frame)

        snapshot = stats.snapshot()
        snapshot["motion"] = motion_score
        snapshot["time"] = time.time()

        print(snapshot)
        time.sleep(0.2)
