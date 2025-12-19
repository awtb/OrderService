from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from order_service.dependencies.auth import get_auth_service
from order_service.dto.auth import LoginRequestDTO
from order_service.dto.auth import TokenPairDTO
from order_service.dto.user import UserDTO
from order_service.schemas.auth import RegistrationRequestSchema
from order_service.schemas.auth import RegistrationResponseSchema
from order_service.schemas.auth import TokenSchema
from order_service.services.auth import AuthService

router = APIRouter(
    tags=["Auth"],
)


@router.post(
    "/register",
    summary="Register a new user",
    response_model=RegistrationResponseSchema,
)
async def register_user(
    data: RegistrationRequestSchema,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserDTO:
    created_user = await auth_service.register(data.to_dto())

    return created_user


@router.post(
    "/auth/token",
    summary="Issue OAuth2 token pair",
    response_model=TokenSchema,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPairDTO:
    dto = LoginRequestDTO(
        email=form_data.username.lower(),
        password=form_data.password,
    )
    return await auth_service.login(dto)
