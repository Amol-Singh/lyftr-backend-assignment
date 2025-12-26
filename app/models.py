# app/models.py
import sqlite3
from datetime import datetime

def get_conn(db_path="/data/app.db"):
    return sqlite3.connect(db_path, check_same_thread=False)

def init_db(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY,
        from_msisdn TEXT NOT NULL,
        to_msisdn TEXT NOT NULL,
        ts TEXT NOT NULL,
        text TEXT,
        created_at TEXT NOT NULL
    );
    """)
    conn.commit()
