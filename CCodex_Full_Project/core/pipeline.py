import argparse
import json
import time
from pathlib import Path

import cv2

from capture.capture_backend import MSSCapture
from capture.window_finder import find_window_by_title_substring, get_client_rect_screen
from core.event_builder import EventBuilder
from core.stats import FarmStats
from core.telemetry import TelemetryExtractor
from output.storage_sqlite import SQLiteStorage


def draw_rois(frame, rois):
    h, w = frame.shape[:2]
    for name, roi in rois.items():
        x = int(roi["x"] * w)
        y = int(roi["y"] * h)
        rw = int(roi["w"] * w)
        rh = int(roi["h"] * h)
        cv2.rectangle(frame, (x, y), (x + rw, y + rh), (0, 255, 0), 1)
        cv2.putText(frame, name, (x, max(16, y - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)


def parse_args():
    parser = argparse.ArgumentParser(description="Read-only live farm analytics")
    parser.add_argument("--layout", default="config/layout.json")
    parser.add_argument("--fps", type=float, default=5.0)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--debug-ocr", action="store_true")
    parser.add_argument("--db", choices=["on", "off"], default="off")
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--snapshot-interval", type=float, default=1.0)
    return parser.parse_args()


def run():
    args = parse_args()
    layout = json.loads(Path(args.layout).read_text(encoding="utf-8"))

    wins = find_window_by_title_substring(layout["window_title_contains"])
    if not wins:
        raise RuntimeError("Fenster nicht gefunden")
    hwnd, title = wins[0]
    print("Nutze Fenster:", title)

    cap = MSSCapture()
    telemetry = TelemetryExtractor(layout)
    events = EventBuilder(layout)
    stats = FarmStats(prices_path="config/prices.json" if Path("config/prices.json").exists() else None)

    storage = None
    if args.db == "on":
        db_path = args.db_path or layout.get("session", {}).get("sqlite_path", "output/farm.db")
        storage = SQLiteStorage(db_path, flush_interval_s=layout.get("session", {}).get("autosave_interval_s", 3))
        storage.write_session_meta({"title": title, "started_at": time.time()})

    frame_delay = 1.0 / max(0.1, args.fps)
    last_snapshot = 0.0

    try:
        while True:
            x, y, w, h = get_client_rect_screen(hwnd)
            frame = cap.grab_region(x, y, w, h)
            t_data = telemetry.extract(frame)
            stats.update_telemetry(t_data)
            new_events = events.build(t_data)
            if new_events and storage:
                storage.write_events(new_events)
            stats.apply_events(new_events)

            now = time.time()
            if now - last_snapshot >= args.snapshot_interval:
                snapshot = stats.snapshot()
                print(json.dumps(snapshot, ensure_ascii=False))
                if storage:
                    storage.write_snapshot(snapshot)
                last_snapshot = now

            if args.debug:
                debug_frame = frame.copy()
                draw_rois(debug_frame, layout.get("rois", {}))
                cv2.imshow("debug-rois", debug_frame)

            if args.debug_ocr:
                rows = []
                for name, dbg in t_data.get("debug", {}).items():
                    img = dbg.get("threshold")
                    if img is None:
                        continue
                    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                    cv2.putText(vis, f"{name}: {dbg.get('raw_text', dbg.get('text', ''))}", (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
                    rows.append(vis)
                if rows:
                    max_w = max(r.shape[1] for r in rows)
                    padded = [cv2.copyMakeBorder(r, 0, 0, 0, max_w - r.shape[1], cv2.BORDER_CONSTANT, value=(0, 0, 0)) for r in rows]
                    panel = cv2.vconcat(padded)
                    cv2.imshow("debug-ocr", panel)

            if args.debug or args.debug_ocr:
                if cv2.waitKey(1) & 0xFF == 27:
                    break

            time.sleep(frame_delay)
    finally:
        if storage:
            storage.close()
        if args.debug or args.debug_ocr:
            cv2.destroyAllWindows()
