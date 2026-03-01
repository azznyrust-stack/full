from vision.ocr import ocr_digits, DigitSmoother
from vision.ocr_text import ocr_text_multiline


def crop(frame, roi):
    h, w = frame.shape[:2]
    x = int(max(0.0, min(1.0, roi["x"])) * w)
    y = int(max(0.0, min(1.0, roi["y"])) * h)
    rw = int(max(0.0, min(1.0, roi["w"])) * w)
    rh = int(max(0.0, min(1.0, roi["h"])) * h)
    return frame[y : y + rh, x : x + rw]


class TelemetryExtractor:
    def __init__(self, layout):
        smoothing = layout.get("smoothing", {})
        self.rois = layout.get("rois", {})
        self.gold_smoother = DigitSmoother(
            window=smoothing.get("median_window", 5),
            max_jump=smoothing.get("max_gold_jump", 5_000_000),
        )

    def extract(self, frame):
        result = {
            "gold": None,
            "chat_text": "",
            "dungeon_text": "",
            "dungeon_counter": None,
            "kill_counter": None,
            "debug": {},
        }

        if "gold_text" in self.rois:
            c = crop(frame, self.rois["gold_text"])
            value, dbg = ocr_digits(c, return_debug=True)
            result["gold"] = self.gold_smoother.update(value)
            result["debug"]["gold_text"] = dbg

        chat_roi = self.rois.get("loot_chat") or self.rois.get("chat_box")
        if chat_roi:
            c = crop(frame, chat_roi)
            txt, dbg = ocr_text_multiline(c)
            result["chat_text"] = txt
            result["debug"]["chat_text"] = dbg

        if "dungeon_status" in self.rois:
            c = crop(frame, self.rois["dungeon_status"])
            txt, dbg = ocr_text_multiline(c)
            result["dungeon_text"] = txt
            result["debug"]["dungeon_status"] = dbg

        if "dungeon_counter" in self.rois:
            c = crop(frame, self.rois["dungeon_counter"])
            value, dbg = ocr_digits(c, return_debug=True)
            result["dungeon_counter"] = value
            result["debug"]["dungeon_counter"] = dbg

        if "kill_counter" in self.rois:
            c = crop(frame, self.rois["kill_counter"])
            value, dbg = ocr_digits(c, return_debug=True)
            result["kill_counter"] = value
            result["debug"]["kill_counter"] = dbg

        return result
