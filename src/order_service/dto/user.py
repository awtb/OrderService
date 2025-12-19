from dataclasses import dataclass

from order_service.dto.base import BaseDTO


@dataclass
class UserDTO(BaseDTO):
    id: str
    email: str
    hashed_password: str


@dataclass
class CurrentUserDTO(BaseDTO):
    id: str
    email: str
