from functools import lru_cache
from typing import AsyncGenerator, Any

from sqlalchemy.ext.asyncio import AsyncSession

from order_service.errors.common import FastApiError
from order_service.settings import Settings


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings


async def get_session(self) -> AsyncGenerator[AsyncSession, Any]:
    session = self.session_maker()
    try:
        yield session
        await session.commit()
    except FastApiError as error:
        await session.rollback()
        raise error
    except Exception as error:
        self.logger.error(self.error_message, exc_info=error)
        await session.rollback()
        raise
    finally:
        await session.close()
