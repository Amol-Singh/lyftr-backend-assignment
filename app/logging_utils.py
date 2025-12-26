# app/logging_utils.py
import json
import logging
from datetime import datetime, timezone

def log_event(**kwargs):
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        **kwargs
    }
    print(json.dumps(record))
