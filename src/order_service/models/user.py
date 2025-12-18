import uuid

from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from order_service.dto.user import UserDTO
from order_service.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(), primary_key=True, nullable=False, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(), nullable=False)

    def to_dto(self) -> UserDTO:
        return UserDTO(
            id=self.id,
            email=self.email,
            hashed_password=self.hashed_password,
        )
