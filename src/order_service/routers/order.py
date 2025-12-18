from fastapi import APIRouter

router = APIRouter(
    tags=["Orders"],
    prefix="/orders",
)


@router.get("/orders")
async def get_orders():
    pass


@router.post("/orders")
async def create_order():
    pass


@router.get("/orders/{order_id}")
async def get_order(order_id: int):
    pass
