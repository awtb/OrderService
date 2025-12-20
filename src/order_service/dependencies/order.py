from fastapi import Depends
from faststream.kafka import KafkaBroker
from order_service.dependencies.common import get_broker
from order_service.dependencies.common import get_redis
from order_service.dependencies.common import get_session
from order_service.repos.order import OrderRepository
from order_service.services.order import OrderService
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession


def get_order_repo(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> OrderRepository:
    return OrderRepository(session, redis)


def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repo),
    broker: KafkaBroker = Depends(get_broker),
) -> OrderService:
    return OrderService(order_repo, broker)
