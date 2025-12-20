from datetime import datetime

from pydantic import BaseModel


class IncomingOrder(BaseModel):
    id: str
    items: dict
    creator_id: str
    created_at: datetime
