from fastapi import Depends
from order_service.dependencies.common import get_session
from order_service.repos.order import OrderRepository
from order_service.services.order import OrderService
from sqlalchemy.ext.asyncio import AsyncSession


def get_order_repo(
    session: AsyncSession = Depends(get_session),
) -> OrderRepository:
    return OrderRepository(session)


def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repo),
) -> OrderService:
    return OrderService(order_repo)
