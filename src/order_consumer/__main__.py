import asyncio
from typing import Any

import uvicorn
from faststream import FastStream
from faststream.asgi import AsgiResponse
from faststream.asgi import get
from faststream.kafka import KafkaBroker
from order_consumer.routers.order import router as order_router
from order_consumer.settings import settings


@get
async def liveness(scope: dict[str, Any]) -> AsgiResponse:
    """Just only for health checks in docker."""
    return AsgiResponse(b"", status_code=204)


broker = KafkaBroker(settings.broker_url)
broker.include_router(order_router)
app = FastStream(broker)


async def main() -> None:
    asgi_routes = [
        ("/internal/alive", liveness),
    ]

    uvicorn_config = uvicorn.Config(
        app.as_asgi(asgi_routes),
        host="0.0.0.0",
        port=8010,
    )
    server = uvicorn.Server(uvicorn_config)
    await server.serve()


asyncio.run(main())
