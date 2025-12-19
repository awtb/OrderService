from order_service.dto.auth import LoginRequestDTO
from order_service.dto.auth import RegistrationRequestDTO
from order_service.schemas.base import BaseSchema
from pydantic import EmailStr
from pydantic import Field


class TokenSchema(BaseSchema):
    token: str = Field(validation_alias="raw_str")
    token_type: str


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


class LoginRequestSchema(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    def to_dto(self) -> LoginRequestDTO:
        return LoginRequestDTO(
            email=str(self.email).lower(),
            password=self.password,
        )
