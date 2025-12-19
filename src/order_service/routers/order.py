from fastapi import APIRouter
from fastapi import Depends
from order_service.dependencies.auth import get_current_user
from order_service.dto.user import CurrentUserDTO

router = APIRouter(
    tags=["Orders"],
    prefix="/orders",
)


@router.get("/orders")
async def get_orders(current_user: CurrentUserDTO = Depends(get_current_user)):
    return current_user


@router.post("/orders")
async def create_order():
    pass


@router.get("/orders/{order_id}")
async def get_order(order_id: int):
    pass
