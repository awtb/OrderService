from order_service.dto.auth import RegistrationRequestDTO
from order_service.schemas.base import BaseSchema
from pydantic import EmailStr
from pydantic import Field


class TokenSchema(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")


class RegistrationRequestSchema(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    def to_dto(self) -> RegistrationRequestDTO:
        return RegistrationRequestDTO(
            email=str(self.email).lower(),
            password=self.password,
        )


class RegistrationResponseSchema(BaseSchema):
    email: str
