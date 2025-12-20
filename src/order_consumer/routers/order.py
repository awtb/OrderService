import asyncio

from faststream.kafka import KafkaRouter
from order_consumer.schemas import IncomingOrder

router = KafkaRouter()


@router.subscriber("new_order")
async def process_incoming_order(incoming_order: IncomingOrder) -> None:
    await asyncio.sleep(2)
    print(f"Order {incoming_order.id} processed")
