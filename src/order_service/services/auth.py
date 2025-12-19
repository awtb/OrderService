from order_service.dto.auth import LoginRequestDTO
from order_service.dto.auth import RegistrationRequestDTO
from order_service.dto.auth import TokenDTO
from order_service.dto.user import UserDTO
from order_service.errors.auth import IncorrectEmailOrPasswordError
from order_service.errors.auth import UserAlreadyExistsError
from order_service.helpers.auth import AuthHelper
from order_service.repos.user import UserRepository


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        auth_helper: AuthHelper,
    ) -> None:
        self._user_repo = user_repo
        self._auth_helper = auth_helper

    async def register(self, data: RegistrationRequestDTO) -> UserDTO:
        user_already_exists = await self._user_repo.user_exists(
            data.email,
        )

        if user_already_exists:
            raise UserAlreadyExistsError()

        hashed_password = self._auth_helper.hash_password(data.password)

        created_user = await self._user_repo.create_user(
            data.email,
            hashed_password,
        )

        return created_user

    async def login(self, data: LoginRequestDTO) -> list[TokenDTO]:
        user = await self._user_repo.get_user_by_email(data.email)

        if user is None:
            raise IncorrectEmailOrPasswordError()

        password_matched = self._auth_helper.verify_password(
            data.password, user.hashed_password
        )

        if not password_matched:
            IncorrectEmailOrPasswordError()

        access_token = self._auth_helper.create_jwt_token(
            "access",
            user.id,
        )
        refresh_token = self._auth_helper.create_jwt_token(
            "refresh",
            user.id,
        )

        return [
            access_token,
            refresh_token,
        ]
