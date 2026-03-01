import argparse
import json
from pathlib import Path

import cv2

from capture.capture_backend import MSSCapture
from capture.window_finder import find_window_by_title_substring, get_client_rect_screen


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--layout", default="config/layout.json")
    return p.parse_args()


def main():
    args = parse_args()
    layout_path = Path(args.layout)
    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    rois = layout.setdefault("rois", {})

    print("Vorhandene ROIs:", ", ".join(sorted(rois.keys())) or "(keine)")

    wins = find_window_by_title_substring(layout["window_title_contains"])
    if not wins:
        raise RuntimeError("Fenster nicht gefunden")
    hwnd, title = wins[0]
    print("Nutze Fenster:", title)

    names = list(rois.keys()) or ["new_roi"]
    idx = 0
    cap = MSSCapture()

    while True:
        x, y, w, h = get_client_rect_screen(hwnd)
        frame = cap.grab_region(x, y, w, h)

        for n, roi in rois.items():
            rx, ry = int(roi["x"] * w), int(roi["y"] * h)
            rw, rh = int(roi["w"] * w), int(roi["h"] * h)
            color = (0, 255, 255) if n == names[idx] else (0, 255, 0)
            cv2.rectangle(frame, (rx, ry), (rx + rw, ry + rh), color, 2)
            cv2.putText(frame, n, (rx, max(16, ry - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        cv2.putText(frame, f"ROI: {names[idx]} | n/p switch | d delete | s save | esc quit", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.imshow("roi-tuner", frame)

        key = cv2.waitKey(30) & 0xFF
        if key == 27:
            break
        if key == ord("n"):
            idx = (idx + 1) % len(names)
        if key == ord("p"):
            idx = (idx - 1) % len(names)
        if key == ord("d") and names:
            target = names[idx]
            rois.pop(target, None)
            names = list(rois.keys()) or ["new_roi"]
            idx = min(idx, len(names) - 1)
            print(f"ROI gelöscht: {target}")
        if key == ord("s"):
            layout_path.write_text(json.dumps(layout, indent=2), encoding="utf-8")
            print("Layout gespeichert:", layout_path)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
