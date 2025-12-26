# app/storage.py
import sqlite3
from datetime import datetime, timezone

def insert_message(conn, msg):
    try:
        conn.execute("""
        INSERT INTO messages 
        (message_id, from_msisdn, to_msisdn, ts, text, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            msg.message_id,
            msg.from_,
            msg.to,
            msg.ts.isoformat(),
            msg.text,
            datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()
        return "created"
    except sqlite3.IntegrityError:
        return "duplicate"
