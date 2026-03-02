import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.roi import crop


class DummyFrame:
    def __init__(self, h, w):
        self.shape = (h, w, 3)

    def __getitem__(self, key):
        ys, xs = key
        h = ys.stop - ys.start
        w = xs.stop - xs.start
        return DummyFrame(h, w)


def main():
    frame = DummyFrame(10, 10)

    roi_zero = {"x": 0.2, "y": 0.2, "w": 0.0, "h": 0.0}
    c1 = crop(frame, roi_zero)
    assert c1.shape[0] >= 1 and c1.shape[1] >= 1

    roi_outside = {"x": 1.2, "y": -0.2, "w": 0.5, "h": 0.5}
    c2 = crop(frame, roi_outside)
    assert c2.shape[0] >= 1 and c2.shape[1] >= 1

    print("ok")


if __name__ == "__main__":
    main()
