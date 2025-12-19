from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from order_service.dependencies.common import get_session
from order_service.dependencies.common import get_settings
from order_service.helpers.auth import AuthHelper
from order_service.repos.user import UserRepository
from order_service.services.auth import AuthService
from order_service.settings import Settings
from sqlalchemy.ext.asyncio import AsyncSession

from src.order_service.dto.user import CurrentUserDTO

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_user_repository(
    session: AsyncSession = Depends(get_session),
) -> UserRepository:
    return UserRepository(session)


def get_auth_helper(settings: Settings = Depends(get_settings)) -> AuthHelper:
    return AuthHelper(
        secret_key=settings.jwt_secret_key,
        hashing_algorithm=settings.jwt_hashing_algorithm,
        access_token_exp=settings.jwt_access_token_expiration_minutes,
        refresh_token_exp=settings.jwt_refresh_token_expiration_minutes,
    )


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    auth_helper: AuthHelper = Depends(get_auth_helper),
) -> AuthService:
    return AuthService(user_repo, auth_helper)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> CurrentUserDTO:
    current_user = auth_service.get_current_user(token)

    return current_user
