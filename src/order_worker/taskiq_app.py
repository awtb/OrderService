from taskiq import TaskiqEvents
from taskiq import TaskiqState
from taskiq_redis import RedisAsyncResultBackend
from taskiq_redis import RedisStreamBroker

from order_worker.settings import settings

result_backend = RedisAsyncResultBackend(settings.redis_dsn)
broker = RedisStreamBroker(settings.redis_dsn).with_result_backend(result_backend)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def worker_startup(state: TaskiqState) -> None:
    print("TaskIQ worker started")


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def worker_shutdown(state: TaskiqState) -> None:
    print("TaskIQ worker stopped")
