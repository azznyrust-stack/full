import re
import time

from core.debounce import EventDebouncer


class EventBuilder:
    def __init__(self, layout):
        parsing = layout.get("parsing", {})
        smoothing = layout.get("smoothing", {})
        self.debouncer = EventDebouncer(
            cooldown_ms=smoothing.get("event_cooldown_ms", 1500),
            stable_frames=smoothing.get("stable_frames", 2),
        )
        self.loot_patterns = [re.compile(p) for p in parsing.get("loot_patterns", [])]
        self.loot_keywords = [k.lower() for k in parsing.get("loot_keywords", [])]
        self.kill_patterns = [re.compile(p) for p in parsing.get("kill_patterns", [])]
        self.kill_keywords = [k.lower() for k in parsing.get("kill_keywords", [])]
        self.start_keywords = [k.lower() for k in parsing.get("dungeon_start_keywords", [])]
        self.end_keywords = [k.lower() for k in parsing.get("dungeon_end_keywords", [])]
        self.prev_gold = None
        self.prev_dungeon_status = ""
        self.prev_kill_counter = None

    def _contains_any(self, text, keywords):
        t = text.lower()
        return any(k in t for k in keywords)

    def build(self, telemetry, now_ts=None):
        now_ts = now_ts if now_ts is not None else time.time()
        now_ms = int(now_ts * 1000)
        events = []

        gold = telemetry.get("gold")
        if gold is not None and self.prev_gold is not None and gold != self.prev_gold:
            delta = gold - self.prev_gold
            kind = "GOLD_GAIN" if delta > 0 else "GOLD_SPEND"
            payload = {"delta": delta, "gold_now": gold}
            h = self.debouncer.make_hash(payload)
            if self.debouncer.allow("gold", h, now_ms):
                events.append({"t": now_ts, "kind": kind, "data": payload})
        if gold is not None:
            self.prev_gold = gold

        chat_text = telemetry.get("chat_text", "") or ""
        for pattern in self.loot_patterns:
            for m in pattern.finditer(chat_text):
                payload = {"text": m.group(0), "item": m.group(1) if m.groups() else m.group(0)}
                h = self.debouncer.make_hash(payload)
                if self.debouncer.allow("loot", h, now_ms):
                    events.append({"t": now_ts, "kind": "LOOT", "data": payload})
        if chat_text and self._contains_any(chat_text, self.loot_keywords):
            payload = {"text": chat_text.splitlines()[-1]}
            h = self.debouncer.make_hash(payload)
            if self.debouncer.allow("loot_kw", h, now_ms):
                events.append({"t": now_ts, "kind": "LOOT", "data": payload})

        dungeon_text = telemetry.get("dungeon_text", "") or ""
        if dungeon_text:
            lower = dungeon_text.lower()
            if self._contains_any(lower, self.start_keywords):
                payload = {"text": dungeon_text}
                h = self.debouncer.make_hash(payload)
                if self.debouncer.allow("dungeon_start", h, now_ms):
                    events.append({"t": now_ts, "kind": "DUNGEON_START", "data": payload})
            if self._contains_any(lower, self.end_keywords):
                payload = {"text": dungeon_text}
                h = self.debouncer.make_hash(payload)
                if self.debouncer.allow("dungeon_end", h, now_ms):
                    events.append({"t": now_ts, "kind": "DUNGEON_END", "data": payload})

        if dungeon_text and dungeon_text != self.prev_dungeon_status:
            payload = {"from": self.prev_dungeon_status, "to": dungeon_text}
            h = self.debouncer.make_hash(payload)
            if self.debouncer.allow("dungeon_state_change", h, now_ms):
                events.append({"t": now_ts, "kind": "DUNGEON_STATE", "data": payload})
            self.prev_dungeon_status = dungeon_text

        kill_counter = telemetry.get("kill_counter")
        if kill_counter is not None and self.prev_kill_counter is not None and kill_counter > self.prev_kill_counter:
            delta = kill_counter - self.prev_kill_counter
            payload = {"delta": delta, "kill_counter": kill_counter}
            h = self.debouncer.make_hash(payload)
            if self.debouncer.allow("kill_counter", h, now_ms):
                events.append({"t": now_ts, "kind": "KILL", "data": payload})
        if kill_counter is not None:
            self.prev_kill_counter = kill_counter

        if chat_text:
            for pattern in self.kill_patterns:
                for m in pattern.finditer(chat_text):
                    payload = {"text": m.group(0)}
                    h = self.debouncer.make_hash(payload)
                    if self.debouncer.allow("kill_text", h, now_ms):
                        events.append({"t": now_ts, "kind": "KILL", "data": payload})
            if self._contains_any(chat_text, self.kill_keywords):
                payload = {"text": chat_text.splitlines()[-1]}
                h = self.debouncer.make_hash(payload)
                if self.debouncer.allow("kill_kw", h, now_ms):
                    events.append({"t": now_ts, "kind": "KILL", "data": payload})

        return events
