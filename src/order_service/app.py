import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from order_service.routers.auth import router as auth_router
from order_service.routers.order import router as order_router
from order_service.settings import Settings
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine


def load_settings(app_instance: FastAPI) -> None:
    settings = Settings()
    app_instance.state.settings = settings


async def setup_db_engine(app_instance: FastAPI) -> None:
    settings: Settings = app_instance.state.settings

    uri = URL.create(
        drivername=settings.db_driver,
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )
    engine = create_async_engine(uri)

    app_instance.state.engine = engine


def setup_logging(app_instance: FastAPI) -> None:
    settings: Settings = app_instance.state.settings
    logging.basicConfig(
        level=settings.logging_lvl,
        format=settings.logging_fmt,
    )


async def remove_engine(app_instance: FastAPI) -> None:
    await app_instance.state.engine.dispose()


@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncGenerator:
    load_settings(app_instance)
    setup_logging(app_instance)
    await setup_db_engine(app_instance)
    yield
    await remove_engine(app_instance)


app = FastAPI(
    title="Order Service",
    description="Order Service",
    version="0.0.1",
    lifespan=lifespan,
)

app.include_router(order_router)
app.include_router(auth_router)
