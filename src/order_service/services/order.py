from dataclasses import asdict

from faststream.kafka import KafkaBroker
from order_service.dto.base import PageDTO
from order_service.dto.order import OrderCreateDTO
from order_service.dto.order import OrderDTO
from order_service.dto.order import OrdersFetchRequestDTO
from order_service.dto.order import UpdateOrderStatusDTO
from order_service.dto.user import CurrentUserDTO
from order_service.errors.common import NotAllowedError
from order_service.errors.common import NotFoundError
from order_service.repos.order import OrderRepository


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        kafka_broker: KafkaBroker,
    ) -> None:
        self._order_repo = order_repo
        self._broker = kafka_broker

    async def create_order(
        self,
        order_create_request: OrderCreateDTO,
    ) -> OrderDTO:
        created_order = await self._order_repo.create_order(
            user_id=order_create_request.current_user.id,
            items=order_create_request.items,
        )

        await self._publish_order(created_order)

        return created_order

    async def fetch_orders(
        self,
        request: OrdersFetchRequestDTO,
    ) -> PageDTO[OrderDTO]:
        return await self._order_repo.fetch_orders(
            page=request.page,
            page_size=request.page_size,
            user_id=request.user_id,
        )

    async def update_order_status(
        self,
        request: UpdateOrderStatusDTO,
    ) -> OrderDTO:
        if request.order.creator_id != request.current_user.id:
            raise NotAllowedError(
                f"You don't have an access to order {request.order.id}"
            )
        updated_order = await self._order_repo.update_order_status(
            request.order, request.status
        )
        return updated_order

    async def get_order_by_id(
        self, order_id: str, current_user: CurrentUserDTO
    ) -> OrderDTO:
        order = await self._order_repo.get_order_by_id(
            order_id,
        )

        if order is None:
            raise NotFoundError(f"order with id = {order_id}")

        if order.creator_id != current_user.id:
            raise NotAllowedError(
                f"You don't have an access to order with id = {order_id}"
            )

        return order

    async def _publish_order(self, created_order: OrderDTO) -> None:
        await self._broker.publish(
            topic="new_order",
            message=asdict(created_order),
        )
