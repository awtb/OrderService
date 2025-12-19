from dataclasses import dataclass
from datetime import datetime

from order_service.dto.base import BaseDTO
from order_service.dto.user import CurrentUserDTO
from order_service.enums.order import OrderStatus


@dataclass
class OrderDTO(BaseDTO):
    id: str
    items: dict
    status: OrderStatus
    created_at: datetime
    creator_id: str


@dataclass
class OrderCreateDTO(BaseDTO):
    items: dict
    current_user: CurrentUserDTO


@dataclass
class UpdateOrderStatusDTO(BaseDTO):
    status: OrderStatus
    order: OrderDTO


@dataclass
class OrdersFetchRequestDTO(BaseDTO):
    page: int
    page_size: int
    user_id: str
