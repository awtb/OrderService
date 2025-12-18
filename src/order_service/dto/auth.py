from dataclasses import dataclass
from typing import Literal

from order_service.dto.base import BaseDTO


@dataclass
class RegistrationResponseDTO(BaseDTO):
    email: str


@dataclass
class RegistrationRequestDTO(BaseDTO):
    email: str
    password: str


@dataclass
class TokenDTO(BaseDTO):
    raw_str: str
    token_type: Literal["access", "refresh"]


@dataclass
class LoginRequestDTO(BaseDTO):
    email: str
    password: str
