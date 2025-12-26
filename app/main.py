# app/main.py
from fastapi import FastAPI, Request, HTTPException, Query
from typing import Optional
from datetime import datetime
from app.config import settings
from app.models import get_conn, init_db
from app.schemas import MessageIn
from app.storage import insert_message
from app.logging_utils import log_event
from app.metrics import http_requests, webhook_results, render_metrics

import hmac, hashlib, uuid, time

app = FastAPI()
conn = None

@app.on_event("startup")
def startup():
    global conn
    if not settings.WEBHOOK_SECRET:
        return
    conn = get_conn()
    init_db(conn)

@app.get("/health/live")
def live():
    return {"status": "alive"}

@app.get("/health/ready")
def ready():
    if not settings.WEBHOOK_SECRET:
        raise HTTPException(503)
    try:
        conn.execute("SELECT 1")
    except:
        raise HTTPException(503)
    return {"status": "ready"}

async def valid_signature(request: Request):
    sig = request.headers.get("X-Signature")
    if not sig:
        return False
    body = await request.body()
    expected = hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, sig)

@app.post("/webhook")
async def webhook(request: Request, payload: MessageIn):
    start = time.time()
    req_id = str(uuid.uuid4())

    if not await valid_signature(request):
        webhook_results["invalid_signature"] += 1
        log_event(
            level="ERROR",
            request_id=req_id,
            path="/webhook",
            status=401,
            result="invalid_signature"
        )
        raise HTTPException(401, detail="invalid signature")

    result = insert_message(conn, payload)
    webhook_results[result] += 1

    log_event(
        level="INFO",
        request_id=req_id,
        path="/webhook",
        status=200,
        message_id=payload.message_id,
        dup=(result == "duplicate"),
        result=result,
        latency_ms=int((time.time() - start) * 1000)
    )
    return {"status": "ok"}

@app.get("/messages")
def get_messages(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    from_: Optional[str] = Query(None, alias="from"),
    since: Optional[datetime] = None,
    q: Optional[str] = None
):
    filters = []
    params = []

    if from_:
        filters.append("from_msisdn = ?")
        params.append(from_)

    if since:
        filters.append("ts >= ?")
        params.append(since.isoformat())

    if q:
        filters.append("LOWER(text) LIKE ?")
        params.append(f"%{q.lower()}%")

    where_clause = ""
    if filters:
        where_clause = "WHERE " + " AND ".join(filters)

    total_query = f"SELECT COUNT(*) FROM messages {where_clause}"
    total = conn.execute(total_query, params).fetchone()[0]

    data_query = f"""
        SELECT message_id, from_msisdn, to_msisdn, ts, text
        FROM messages
        {where_clause}
        ORDER BY ts ASC, message_id ASC
        LIMIT ? OFFSET ?
    """
    rows = conn.execute(
        data_query, params + [limit, offset]
    ).fetchall()

    data = [
        {
            "message_id": r[0],
            "from": r[1],
            "to": r[2],
            "ts": r[3],
            "text": r[4]
        }
        for r in rows
    ]

    return {
        "data": data,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/stats")
def get_stats():
    total_messages = conn.execute(
        "SELECT COUNT(*) FROM messages"
    ).fetchone()[0]

    if total_messages == 0:
        return {
            "total_messages": 0,
            "senders_count": 0,
            "messages_per_sender": [],
            "first_message_ts": None,
            "last_message_ts": None
        }

    senders_count = conn.execute(
        "SELECT COUNT(DISTINCT from_msisdn) FROM messages"
    ).fetchone()[0]

    sender_rows = conn.execute("""
        SELECT from_msisdn, COUNT(*) as cnt
        FROM messages
        GROUP BY from_msisdn
        ORDER BY cnt DESC
        LIMIT 10
    """).fetchall()

    messages_per_sender = [
        {"from": r[0], "count": r[1]} for r in sender_rows
    ]

    first_ts, last_ts = conn.execute("""
        SELECT MIN(ts), MAX(ts) FROM messages
    """).fetchone()

    return {
        "total_messages": total_messages,
        "senders_count": senders_count,
        "messages_per_sender": messages_per_sender,
        "first_message_ts": first_ts,
        "last_message_ts": last_ts
    }



@app.get("/metrics")
def metrics():
    return render_metrics()
