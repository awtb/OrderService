from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import Query
from order_service.dependencies.auth import get_current_user
from order_service.dependencies.order import get_order_service
from order_service.dto.base import PageDTO
from order_service.dto.order import OrderCreateDTO
from order_service.dto.order import OrderDTO
from order_service.dto.order import OrdersFetchRequestDTO
from order_service.dto.order import UpdateOrderStatusDTO
from order_service.dto.user import CurrentUserDTO
from order_service.schemas.order import OrderCreateRequestSchema
from order_service.schemas.order import OrderSchema
from order_service.schemas.order import OrderStatusUpdateSchema
from order_service.services.order import OrderService

router = APIRouter(
    tags=["Orders"],
    prefix="/orders",
)


@router.get("/orders/user/{user_id}", summary="Get my orders")
async def get_orders(
    user_id: str = Path(title="User ID"),
    page: int = Query(title="Page", description="Page number", gt=0),
    page_size: int = Query(title="Page Size", description="Page size", gt=0),
    order_service: OrderService = Depends(get_order_service),
) -> PageDTO[OrderDTO]:
    orders_fetch_request = OrdersFetchRequestDTO(
        page=page,
        page_size=page_size,
        user_id=user_id,
    )
    result = await order_service.fetch_orders(
        orders_fetch_request,
    )

    return result


@router.post(
    "/orders",
    response_model=OrderSchema,
    summary="Create a new order",
)
async def create_order(
    data: OrderCreateRequestSchema,
    current_user: CurrentUserDTO = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderDTO:
    dto = OrderCreateDTO(
        items=data.items,
        current_user=current_user,
    )

    created_order = await order_service.create_order(
        dto,
    )

    return created_order


@router.get("/orders/{order_id}", summary="Get Order by id")
async def get_order(
    order_id: str = Path(title="Order ID"),
    current_user: CurrentUserDTO = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderDTO:
    return await order_service.get_order_by_id(
        order_id=order_id,
        current_user=current_user,
    )


@router.patch(
    "/orders/{order_id}",
    response_model=OrderSchema,
)
async def update_order(
    data: OrderStatusUpdateSchema,
    order: OrderDTO = Depends(get_order),
    current_user: CurrentUserDTO = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderDTO:
    dto = UpdateOrderStatusDTO(
        status=data.status,
        order=order,
        current_user=current_user,
    )
    updated_order = await order_service.update_order_status(dto)
    return updated_order
