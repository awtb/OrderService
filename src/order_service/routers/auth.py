from fastapi import APIRouter
from fastapi import Depends
from order_service.dependencies.auth import get_auth_service
from order_service.dto.user import UserDTO
from order_service.schemas.auth import RegistrationRequestSchema
from order_service.schemas.auth import RegistrationResponseSchema
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
