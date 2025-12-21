from order_service.dto.user import UserDTO
from order_service.models.base import BaseModel
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from ulid import ULID


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(), primary_key=True, nullable=False, default=lambda: str(ULID())
    )
    email: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(), nullable=False)

    def to_dto(self) -> UserDTO:
        return UserDTO(
            id=self.id,
            email=self.email,
            hashed_password=self.hashed_password,
        )
