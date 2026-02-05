import asyncio

from order_worker.taskiq_app import broker


@broker.task
async def process_incoming_order(payload: dict) -> None:
    await asyncio.sleep(2)
    print(f"Order {payload['id']} processed", flush=True)
