import csv
import json
import time
from pathlib import Path


class FarmStats:
    def __init__(self, prices_path=None, csv_path=None):
        self.started_at = time.time()
        self.gold_start = None
        self.gold_now = None
        self.gains = 0
        self.spends = 0
        self.monsters_killed = 0
        self.dungeons_done = 0
        self.loot_items = []
        self.prices = self._load_prices(prices_path)
        self.csv_path = csv_path
        if self.csv_path:
            self._init_csv()

    def _load_prices(self, prices_path):
        if not prices_path:
            return {}
        path = Path(prices_path)
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _init_csv(self):
        path = Path(self.csv_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            with path.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=["t", "gold_now", "gold_profit", "monsters_killed", "dungeons_done"])
                writer.writeheader()

    def _append_csv(self, snapshot):
        if not self.csv_path:
            return
        with Path(self.csv_path).open("a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=["t", "gold_now", "gold_profit", "monsters_killed", "dungeons_done"])
            writer.writerow(
                {
                    "t": snapshot["time"],
                    "gold_now": snapshot["gold_now"],
                    "gold_profit": snapshot["gold_profit"],
                    "monsters_killed": snapshot["monsters_killed"],
                    "dungeons_done": snapshot["dungeons_done"],
                }
            )

    def update_telemetry(self, telemetry):
        gold = telemetry.get("gold")
        if gold is None:
            return
        if self.gold_start is None:
            self.gold_start = gold
        self.gold_now = gold

    def apply_events(self, events):
        for event in events:
            kind = event["kind"]
            data = event.get("data", {})
            if kind == "GOLD_GAIN":
                self.gains += max(0, int(data.get("delta", 0)))
            elif kind == "GOLD_SPEND":
                self.spends += abs(min(0, int(data.get("delta", 0))))
            elif kind == "KILL":
                self.monsters_killed += max(1, int(data.get("delta", 1)))
            elif kind == "DUNGEON_END":
                self.dungeons_done += 1
            elif kind == "LOOT":
                item = data.get("item") or data.get("text")
                if item:
                    self.loot_items.append(item)

    def snapshot(self):
        now = time.time()
        runtime = max(1e-9, now - self.started_at)
        gold_profit = self.gains - self.spends
        loot_value = sum(self.prices.get(item, 0) for item in self.loot_items)
        snap = {
            "time": now,
            "runtime_s": runtime,
            "gold_start": self.gold_start,
            "gold_now": self.gold_now,
            "gold_profit": gold_profit,
            "monsters_killed": self.monsters_killed,
            "dungeons_done": self.dungeons_done,
            "kills_per_hour": self.monsters_killed * 3600.0 / runtime,
            "dungeons_per_hour": self.dungeons_done * 3600.0 / runtime,
            "profit_per_hour": gold_profit * 3600.0 / runtime,
            "loot_value": loot_value if self.prices else None,
        }
        self._append_csv(snap)
        return snap
