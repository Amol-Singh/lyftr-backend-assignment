# app/schemas.py
from pydantic import BaseModel, Field
from pydantic import StringConstraints
from typing import Optional, Annotated
from datetime import datetime, timezone

E164String = Annotated[str, StringConstraints(pattern=r"^\+\d+$")]

class MessageIn(BaseModel):
    message_id: Annotated[str, StringConstraints(min_length=1)]
    from_: E164String = Field(alias="from")
    to: E164String
    ts: datetime
    text: Optional[Annotated[str, StringConstraints(max_length=4096)]] = None

    @staticmethod
    def _validate_ts(v: datetime):
        if v.tzinfo != timezone.utc:
            raise ValueError("ts must be UTC")
        return v

    model_config = {
        "populate_by_name": True
    }
