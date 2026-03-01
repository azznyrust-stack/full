
class FarmStats:
    def __init__(self):
        self.gold_start = None
        self.gold_current = None
        self.gold_profit = 0
        self.events = []

    def update_gold(self, gold):
        if gold is None:
            return
        if self.gold_start is None:
            self.gold_start = gold
        if self.gold_current is not None:
            delta = gold - self.gold_current
            if delta > 0:
                self.gold_profit += delta
        self.gold_current = gold

    def snapshot(self):
        return {
            "gold_start": self.gold_start,
            "gold_current": self.gold_current,
            "gold_profit": self.gold_profit
        }
