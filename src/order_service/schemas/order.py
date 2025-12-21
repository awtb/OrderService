from datetime import datetime

from ..enums.order import OrderStatus
from .base import BaseSchema


class OrderCreateRequestSchema(BaseSchema):
    items: dict
    order_price: float


class OrderSchema(BaseSchema):
    id: str
    items: dict
    status: OrderStatus
    created_at: datetime
    creator_id: str
    order_price: float


class OrderStatusUpdateSchema(BaseSchema):
    status: OrderStatus
