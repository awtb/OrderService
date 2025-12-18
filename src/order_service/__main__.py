from fastapi import FastAPI
from order_service.routers.auth import router as auth_router
from order_service.routers.order import router as order_router

app = FastAPI(
    title="Order Service",
    description="Order Service",
    version="0.0.1",
)

app.include_router(order_router)
app.include_router(auth_router)
