def crop(frame, roi):
    h, w = frame.shape[:2]
    if h == 0 or w == 0:
        return frame

    x = int(max(0.0, min(1.0, roi["x"])) * w)
    y = int(max(0.0, min(1.0, roi["y"])) * h)
    rw = max(1, int(max(0.0, min(1.0, roi["w"])) * w))
    rh = max(1, int(max(0.0, min(1.0, roi["h"])) * h))

    x = min(max(0, x), w - 1)
    y = min(max(0, y), h - 1)
    rw = min(rw, w - x)
    rh = min(rh, h - y)

    return frame[y : y + rh, x : x + rw]
