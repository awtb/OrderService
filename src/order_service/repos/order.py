import json
import logging
from datetime import datetime
from typing import Any

from order_service.dto.base import PageDTO
from order_service.dto.order import OrderDTO
from order_service.enums.order import OrderStatus
from order_service.models import Order
from order_service.repos.base import BaseRepository
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession


class OrderRepository(BaseRepository):
    def __init__(
        self,
        session: AsyncSession,
        redis: Redis,
        warmup_ttl_seconds: int = 300,
    ) -> None:
        self._redis = redis
        self._ttl = warmup_ttl_seconds
        super().__init__(session)

    async def get_order_by_id(self, order_id: str) -> OrderDTO | None:
        cached = await self._cache_get(order_id)
        if cached:
            logging.debug(
                "Order %s loaded from cache",
                order_id,
            )
            return cached

        logging.debug(
            "Order %s loaded from db",
            order_id,
        )

        obj = await self._db_get(order_id)
        if not obj:
            return None

        dto = obj.to_dto()
        await self._cache_set(dto)
        return dto

    async def create_order(
        self,
        user_id: str,
        items: dict[str, Any],
    ) -> OrderDTO:
        order_obj = Order(user_id=user_id, items=items)

        self._session.add(order_obj)
        await self._session.flush()
        await self._session.refresh(order_obj)

        dto = order_obj.to_dto()
        await self._cache_set(dto)
        return dto

    async def update_order_status(
        self, order: OrderDTO, new_status: OrderStatus
    ) -> OrderDTO:
        stmt = (
            update(Order)
            .where(Order.id == order.id)
            .values(status=new_status)
            .returning(Order)
        )

        result = await self._session.execute(stmt)
        await self._session.flush()

        updated_obj = result.scalar_one()
        dto = updated_obj.to_dto()

        await self._cache_set(dto)
        return dto

    async def fetch_orders(
        self, page_size: int, page: int, user_id: str
    ) -> PageDTO[OrderDTO]:
        stmt = select(Order).where(Order.user_id == user_id)
        return await self._fetch(
            query=stmt,
            page_size=page_size,
            page=page,
            mapper_fn=lambda x: x.to_dto(),
        )

    async def _db_get(self, order_id: str) -> Order | None:
        stmt = select(Order).where(Order.id == order_id)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def _cache_get(self, order_id: str) -> OrderDTO | None:
        key = self._order_key(order_id)
        payload = await self._redis.hgetall(key)
        if not payload:
            return None
        try:
            return self._load_order(payload)
        except Exception:
            return None

    async def _cache_set(self, order: OrderDTO) -> None:
        key = self._order_key(order.id)
        data = self._dump_order(order)
        pipe = self._redis.pipeline(transaction=False)
        pipe.hset(key, mapping=data)  # type: ignore
        pipe.expire(key, time=self._ttl)
        await pipe.execute()

    @staticmethod
    def _order_key(order_id: str) -> str:
        return f"order:{order_id}"

    @staticmethod
    def _dump_order(order: OrderDTO) -> dict[str, str]:
        return {
            "id": str(order.id),
            "creator_id": str(order.creator_id),
            "status": str(order.status),
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "items": json.dumps(
                order.items,
                separators=(",", ":"),
                ensure_ascii=False,
            ),
        }

    @staticmethod
    def _load_order(payload: dict[str, str]) -> OrderDTO:
        return OrderDTO(
            id=payload["id"],
            status=OrderStatus(payload["status"]),
            created_at=datetime.strptime(
                payload["created_at"],
                "%Y-%m-%d %H:%M:%S",
            ),
            items=json.loads(payload["items"]),
            creator_id=payload["creator_id"],
        )
