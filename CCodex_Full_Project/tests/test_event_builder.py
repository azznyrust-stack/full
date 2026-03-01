import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.event_builder import EventBuilder


LAYOUT = {
    "parsing": {
        "loot_patterns": [r"(?i)you received\s+(.+)"],
        "loot_keywords": ["received"],
        "kill_patterns": [r"(?i)you killed\s+(.+)"],
        "kill_keywords": ["killed"],
        "dungeon_start_keywords": ["dungeon start"],
        "dungeon_end_keywords": ["dungeon completed"],
    },
    "smoothing": {"event_cooldown_ms": 1, "stable_frames": 1},
}


def main():
    b = EventBuilder(LAYOUT)
    telemetry = {
        "gold": 1000,
        "chat_text": "You received Magic Sword\nYou killed Slime",
        "dungeon_text": "Dungeon start",
        "kill_counter": 1,
    }
    first = b.build(telemetry, now_ts=1.0)
    assert any(e["kind"] == "LOOT" for e in first)
    assert any(e["kind"] == "KILL" for e in first)
    assert any(e["kind"] == "DUNGEON_START" for e in first)

    second = b.build({**telemetry, "gold": 1100, "dungeon_text": "Dungeon completed", "kill_counter": 2}, now_ts=2.0)
    assert any(e["kind"] == "GOLD_GAIN" for e in second)
    assert any(e["kind"] == "DUNGEON_END" for e in second)

    print("ok")


if __name__ == "__main__":
    main()
