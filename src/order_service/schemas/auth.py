from pydantic import EmailStr

from order_service.dto.auth import RegistrationRequestDTO
from order_service.schemas.base import BaseSchema


class RegistrationRequestSchema(BaseSchema):
    email: EmailStr
    password: str

    def to_dto(self) -> RegistrationRequestDTO:
        return RegistrationRequestDTO(
            email=str(self.email).lower(),
            password=self.password,
        )


class RegistrationResponseSchema(BaseSchema):
    email: str
