from order_service.dto.base import PageDTO
from order_service.dto.order import OrderDTO
from order_service.enums.order import OrderStatus
from order_service.models import Order
from order_service.repos.base import BaseRepository
from sqlalchemy import select
from sqlalchemy import update


class OrderRepository(BaseRepository):
    async def get_order_by_id(self, order_id: str) -> OrderDTO | None:
        stmt = select(Order).where(Order.id == order_id)

        results = await self._session.execute(stmt)
        first = results.scalars().first()

        return first.to_dto() if first else None

    async def create_order(self, user_id: str, items: dict) -> OrderDTO:
        order_obj = Order(user_id=user_id, items=items)

        self._session.add(order_obj)
        await self._session.refresh(order_obj)
        return order_obj.to_dto()

    async def update_order_status(
        self, order: OrderDTO, new_status: OrderStatus
    ) -> OrderDTO:
        stmt = (
            update(Order)
            .where(Order.id == order.id)
            .values(
                status=new_status,
            )
        )
        await self._session.execute(stmt)
        await self._session.flush()

        updated_order = await self.get_order_by_id(order.id)

        return updated_order

    async def fetch_orders(
        self, page_size: int, page: int, user_id: str
    ) -> PageDTO[OrderDTO]:
        stmt = select(Order).where(Order.user_id == user_id)
        page = await self._fetch(
            stmt,
            page_size,
            page,
            mapper_fn=lambda x: x.to_dto(),
        )

        return page
