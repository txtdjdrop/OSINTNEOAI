import sqlite3
import os
import json
from datetime import datetime

DB_PATH = "/home/brainmedus_gmail_com/OsintNeoAi/data/chat_history.db"

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sql TEXT NOT NULL,
            result_count INTEGER,
            execution_time_ms REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_message(role, content, metadata=None):
    conn = get_db()
    conn.execute(
        "INSERT INTO messages (role, content, metadata) VALUES (?, ?, ?)",
        (role, content, json.dumps(metadata or {}))
    )
    conn.commit()
    conn.close()

def get_history(limit=50):
    conn = get_db()
    rows = conn.execute(
        "SELECT role, content, created_at FROM messages ORDER BY created_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]

def save_query(sql, result_count, execution_time_ms):
    conn = get_db()
    conn.execute(
        "INSERT INTO queries (sql, result_count, execution_time_ms) VALUES (?, ?, ?)",
        (sql, result_count, execution_time_ms)
    )
    conn.commit()
    conn.close()

def get_query_stats():
    conn = get_db()
    row = conn.execute(
        "SELECT COUNT(*) as total, SUM(result_count) as total_rows FROM queries"
    ).fetchone()
    conn.close()
    return dict(row) if row else {"total": 0, "total_rows": 0}
