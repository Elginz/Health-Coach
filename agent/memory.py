"""
agent/memory.py
Simple SQLite-backed memory for:
- messages (keep timestamps + role + text)
- weights (date, weight_kg)
Provides helper methods to keep last-10 messages retrieval convenient.
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime

DB_DIR = Path(__file__).resolve().parents[1] / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "coach.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    ts TEXT NOT NULL,
    role TEXT NOT NULL,
    text TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_user_ts ON messages (user_id, ts);

CREATE TABLE IF NOT EXISTS weights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date TEXT NOT NULL,
    weight_kg REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_weights_user_date ON weights (user_id, date);
"""

class Memory:
    def __init__(self, db_path: Optional[str] = None):
        self._db = sqlite3.connect(str(db_path or DB_PATH), check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        cur = self._db.cursor()
        cur.executescript(_SCHEMA)
        self._db.commit()

    # Message methods
    def add_message(self, user_id: str, role: str, text: str):
        ts = datetime.utcnow().isoformat()
        cur = self._db.cursor()
        cur.execute("INSERT INTO messages (user_id, ts, role, text) VALUES (?, ?, ?, ?)", (user_id, ts, role, text))
        self._db.commit()
        # prune to last 200 messages overall (optional); for per-user retrieval we'll fetch last 10
        return cur.lastrowid

    def get_last_messages(self, user_id: str, limit: int = 10) -> List[dict]:
        cur = self._db.cursor()
        cur.execute("SELECT ts, role, text FROM messages WHERE user_id = ? ORDER BY ts DESC LIMIT ?", (user_id, limit))
        rows = cur.fetchall()
        # return in chronological order
        return [dict(r) for r in reversed(rows)]

    # Weight methods
    def log_weight(self, user_id: str, date_str: str, weight_kg: float):
        cur = self._db.cursor()
        cur.execute("INSERT INTO weights (user_id, date, weight_kg) VALUES (?, ?, ?)", (user_id, date_str, weight_kg))
        self._db.commit()
        return cur.lastrowid

    def get_last_weight(self, user_id: str) -> Optional[float]:
        cur = self._db.cursor()
        cur.execute("SELECT weight_kg FROM weights WHERE user_id = ? ORDER BY date DESC LIMIT 1", (user_id,))
        r = cur.fetchone()
        return float(r["weight_kg"]) if r else None

    def get_weight_history(self, user_id: str, limit: int = 50) -> List[dict]:
        cur = self._db.cursor()
        cur.execute("SELECT date, weight_kg FROM weights WHERE user_id = ? ORDER BY date ASC LIMIT ?", (user_id, limit))
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    def close(self):
        self._db.close()
