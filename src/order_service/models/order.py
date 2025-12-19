from datetime import datetime

import ulid
from order_service.dto.order import OrderDTO
from order_service.enums.order import OrderStatus
from order_service.models.base import BaseModel
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column


class Order(BaseModel):
    __tablename__ = "order"

    id: Mapped[str] = mapped_column(
        String(), primary_key=True, default=lambda: str(ulid.ULID())
    )
    user_id: Mapped[str] = mapped_column(
        String(), ForeignKey("users.id"), nullable=False
    )
    items: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    def to_dto(self) -> OrderDTO:
        return OrderDTO(
            id=self.id,
            created_at=self.created_at,
            status=self.status,
            creator_id=self.user_id,
            items=self.items,
        )
