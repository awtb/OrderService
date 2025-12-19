from datetime import datetime

from ..enums.order import OrderStatus
from .base import BaseSchema


class OrderCreateRequestSchema(BaseSchema):
    items: dict


class OrderSchema(BaseSchema):
    id: str
    items: dict
    status: OrderStatus
    created_at: datetime
    creator_id: str


class OrderStatusUpdateSchema(BaseSchema):
    status: OrderStatus
