import logging
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Depends
from fastapi import Request
from faststream.kafka import KafkaBroker
from order_service.errors.common import FastApiError
from order_service.settings import Settings
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_session_maker(request: Request) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=request.app.state.engine,
        expire_on_commit=False,
    )


def get_redis(request: Request) -> Redis:
    pool = request.app.state.redis_connection_pool

    return Redis(connection_pool=pool)


def get_broker(request: Request) -> KafkaBroker:
    return request.app.state.broker


async def get_session(
    session_maker: async_sessionmaker[AsyncSession] = Depends(
        get_session_maker,
    ),
) -> AsyncGenerator[AsyncSession, Any]:
    session = session_maker()
    try:
        yield session
        await session.commit()
    except FastApiError as error:
        await session.rollback()
        raise error
    except Exception as error:
        logging.error(msg="An error occurred", exc_info=error)
        await session.rollback()
        raise
    finally:
        await session.close()
