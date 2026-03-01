import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.debounce import EventDebouncer


def main():
    d = EventDebouncer(cooldown_ms=1000, stable_frames=2)
    h = d.make_hash({"a": 1})

    assert d.allow("x", h, now_ms=0) is False
    assert d.allow("x", h, now_ms=10) is True
    assert d.allow("x", h, now_ms=100) is False
    assert d.allow("x", h, now_ms=1200) is True
    print("ok")


if __name__ == "__main__":
    main()
