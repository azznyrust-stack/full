import hashlib
import time
from collections import defaultdict


class EventDebouncer:
    def __init__(self, cooldown_ms=1000, stable_frames=2):
        self.cooldown_ms = cooldown_ms
        self.stable_frames = stable_frames
        self._last_emit_ms = {}
        self._last_hash = {}
        self._stable_count = defaultdict(int)

    @staticmethod
    def make_hash(payload):
        raw = str(payload).encode("utf-8", errors="ignore")
        return hashlib.sha1(raw).hexdigest()

    def allow(self, key, payload_hash, now_ms=None):
        now_ms = now_ms if now_ms is not None else int(time.time() * 1000)
        cache_key = f"{key}:{payload_hash}"

        last_hash = self._last_hash.get(key)
        if last_hash == payload_hash:
            self._stable_count[cache_key] += 1
        else:
            self._last_hash[key] = payload_hash
            self._stable_count[cache_key] = 1

        if self._stable_count[cache_key] < self.stable_frames:
            return False

        if cache_key in self._last_emit_ms:
            elapsed = now_ms - self._last_emit_ms[cache_key]
            if elapsed < self.cooldown_ms:
                return False

        self._last_emit_ms[cache_key] = now_ms
        return True
