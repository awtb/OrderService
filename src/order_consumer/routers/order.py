from faststream.kafka import KafkaRouter
from order_consumer.schemas import IncomingOrder
from order_worker.tasks import process_incoming_order as process_order_task

router = KafkaRouter()


@router.subscriber("new_order")
async def process_incoming_order(incoming_order: IncomingOrder) -> None:
    await process_order_task.kiq(incoming_order.model_dump())
