from fastapi import APIRouter
from fastapi import Depends
from order_service.dependencies.auth import get_current_user
from order_service.dependencies.order import get_order_service
from order_service.dto.order import OrderCreateDTO
from order_service.dto.order import OrderDTO
from order_service.dto.user import CurrentUserDTO
from order_service.schemas.order import OrderCreateRequestSchema
from order_service.schemas.order import OrderSchema
from order_service.services.order import OrderService

router = APIRouter(
    tags=["Orders"],
    prefix="/orders",
)


@router.get("/orders", summary="Get my orders")
async def get_orders(current_user: CurrentUserDTO = Depends(get_current_user)):
    return current_user


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


@router.get("/orders/{order_id}")
async def get_order(order_id: int):
    pass
