# ════════════════════════════════════════
#  Satoru — قاعدة البيانات (SQLite)
# ════════════════════════════════════════
import sqlite3
import json
import os
from typing import Any, Optional, Set, List

DB_PATH = os.path.join(os.path.dirname(__file__), "satoru_data.db")

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
        # key-value عام
        c.execute("""
            CREATE TABLE IF NOT EXISTS kv (
                key   TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        # sets (قوائم مثل المكتومين والاختصارات)
        c.execute("""
            CREATE TABLE IF NOT EXISTS sets (
                key   TEXT,
                value TEXT,
                PRIMARY KEY (key, value)
            )
        """)
        self.conn.commit()

    # ── Key-Value ──
    def get(self, key: str, default=None):
        row = self.conn.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
        if row is None:
            return default
        try:
            return json.loads(row[0])
        except Exception:
            return row[0]

    def set(self, key: str, value: Any):
        self.conn.execute(
            "INSERT OR REPLACE INTO kv (key,value) VALUES (?,?)",
            (key, json.dumps(value, ensure_ascii=False))
        )
        self.conn.commit()

    def delete(self, key: str):
        self.conn.execute("DELETE FROM kv WHERE key=?", (key,))
        self.conn.commit()

    def exists(self, key: str) -> bool:
        return self.conn.execute("SELECT 1 FROM kv WHERE key=?", (key,)).fetchone() is not None

    # ── Sets ──
    def sadd(self, key: str, *values):
        for v in values:
            self.conn.execute(
                "INSERT OR IGNORE INTO sets (key,value) VALUES (?,?)",
                (key, str(v))
            )
        self.conn.commit()

    def srem(self, key: str, *values):
        for v in values:
            self.conn.execute("DELETE FROM sets WHERE key=? AND value=?", (key, str(v)))
        self.conn.commit()

    def smembers(self, key: str) -> Set[str]:
        rows = self.conn.execute("SELECT value FROM sets WHERE key=?", (key,)).fetchall()
        return {r[0] for r in rows}

    def sismember(self, key: str, value) -> bool:
        return self.conn.execute(
            "SELECT 1 FROM sets WHERE key=? AND value=?", (key, str(value))
        ).fetchone() is not None

    def sdelete(self, key: str):
        self.conn.execute("DELETE FROM sets WHERE key=?", (key,))
        self.conn.commit()

    # ── Helpers ──
    def keys_like(self, pattern: str) -> List[str]:
        sql_pattern = pattern.replace("*", "%")
        rows = self.conn.execute("SELECT key FROM kv WHERE key LIKE ?", (sql_pattern,)).fetchall()
        return [r[0] for r in rows]


db = Database()
