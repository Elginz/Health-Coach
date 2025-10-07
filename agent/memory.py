# agent/memory.py
import sqlite3
from datetime import datetime
from typing import List, Dict

DB_PATH = "data/memory.sqlite"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        role TEXT,
        text TEXT,
        ts TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_message(user_id: str, role: str, text: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO messages(user_id, role, text, ts) VALUES (?,?,?,?)",
              (user_id, role, text, datetime.utcnow().isoformat() + "Z"))
    conn.commit()
    conn.close()
    _trim_to_last_n(user_id, 10)

def _trim_to_last_n(user_id: str, n: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM messages WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = c.fetchall()
    if len(rows) > n:
        ids_to_remove = [r[0] for r in rows[n:]]
        c.executemany("DELETE FROM messages WHERE id = ?", [(i,) for i in ids_to_remove])
    conn.commit()
    conn.close()

def get_last_messages(user_id: str, limit: int = 10) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT role, text, ts FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return [{"role": r[0], "text": r[1], "ts": r[2]} for r in reversed(rows)]
