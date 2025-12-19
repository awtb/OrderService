from order_service.dto.order import OrderCreateDTO
from order_service.dto.order import OrderDTO
from order_service.repos.order import OrderRepository


class OrderService:
    def __init__(self, order_repo: OrderRepository) -> None:
        self._order_repo = order_repo

    async def create_order(
        self,
        order_create_request: OrderCreateDTO,
    ) -> OrderDTO:
        created_order = await self._order_repo.create_order(
            user_id=order_create_request.current_user.id,
            items=order_create_request.items,
        )

        return created_order
