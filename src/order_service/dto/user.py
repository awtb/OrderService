from dataclasses import dataclass

from order_service.dto.base import BaseDTO


@dataclass
class UserDTO(BaseDTO):
    id: str
    email: str
    hashed_password: str
