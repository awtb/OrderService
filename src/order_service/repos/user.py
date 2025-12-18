from sqlalchemy import select, exists

from order_service.dto.user import UserDTO
from order_service.models.user import User
from order_service.repos.base import BaseRepository


class UserRepository(BaseRepository):
    async def user_exists(self, email: str) -> bool:
        stmt = select(exists(User).where(User.email == email))
        res = await self._session.execute(stmt)

        return res.scalars().first()

    async def create_user(self, email: str, hashed_password: str) -> UserDTO:
        model = User(
            email=email,
            hashed_password=hashed_password,
        )
        self._session.add(model)

        await self._session.commit()
        return model.to_dto()

    async def get_user_by_email(self, email: str) -> UserDTO | None:
        stmt = select(User).where(User.email == email)

        res = await self._session.execute(stmt)
        first_row = res.first()

        return first_row.to_dto() if first_row else None
