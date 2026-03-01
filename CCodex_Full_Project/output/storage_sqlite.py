import json
import sqlite3
import time
from pathlib import Path


class SQLiteStorage:
    def __init__(self, db_path, flush_interval_s=3):
        self.db_path = Path(db_path)
        self.flush_interval_s = flush_interval_s
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()
        self._create_schema()
        self.last_flush = time.time()

    def _create_schema(self):
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS events (t REAL, kind TEXT, data_json TEXT)"
        )
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS snapshots (t REAL, data_json TEXT)"
        )
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS session (meta TEXT)"
        )
        self.conn.commit()

    def write_session_meta(self, meta):
        self.cur.execute("INSERT INTO session(meta) VALUES (?)", (json.dumps(meta),))

    def write_events(self, events):
        for ev in events:
            self.cur.execute(
                "INSERT INTO events(t, kind, data_json) VALUES (?, ?, ?)",
                (ev["t"], ev["kind"], json.dumps(ev.get("data", {}))),
            )
        self._maybe_flush()

    def write_snapshot(self, snapshot):
        self.cur.execute(
            "INSERT INTO snapshots(t, data_json) VALUES (?, ?)",
            (snapshot["time"], json.dumps(snapshot)),
        )
        self._maybe_flush()

    def _maybe_flush(self):
        if time.time() - self.last_flush >= self.flush_interval_s:
            self.conn.commit()
            self.last_flush = time.time()

    def close(self):
        self.conn.commit()
        self.conn.close()
