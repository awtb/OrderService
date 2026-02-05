# Order Service

Asynchronous FastAPI platform dedicated to the lifecycle of customer orders. It authenticates users, issues JWT token pairs, stores order data, caches frequently accessed records, and publishes every new order to Kafka so downstream services can keep up in real time.

## Goals

- **Operate entirely from Docker** so onboarding requires nothing more than `docker compose up`.
- **Protect the API surface** with OAuth2 password flow, hashed passwords, and signed JWT access/refresh tokens.
- **Guarantee responsiveness** through async SQLAlchemy with Redis-backed read-through caching.
- **Emit domain events** to Kafka so other services can react to `new_order` messages immediately.
- **Simplify observability & reliability** using SlowAPI rate limits, structured logging, and health checks.

## Architecture At A Glance

- **API (`order_service`)** – FastAPI app started via Typer (`python -m order_service`). Lifespan hooks wire PostgreSQL, Redis, Kafka, logging, and SlowAPI rate limits.
- **Database & Cache** – PostgreSQL for persistence, Redis for hot `Order` lookups (key format `order:<id>`).
- **Messaging** – Kafka topic `new_order` receives an event after every successful `POST /orders` call.
- **Worker (`order_consumer`)** – FastStream + uvicorn app that subscribes to `new_order` and enqueues TaskIQ jobs backed by Redis.
- **Infrastructure** – Dockerfile installs Python 3.14 and [uv](https://github.com/astral-sh/uv); `compose.yaml` orchestrates Postgres, Redis, Kafka, Zookeeper, API, and consumer services.

```
FastAPI (Auth + Orders)
 ├── PostgreSQL (orders, users)
 ├── Redis cache (warm orders)
 ├── KafkaBroker (topic=new_order)
 └── SlowAPI limiter

FastStream consumer
 ├── Kafka subscriber -> enqueue TaskIQ job
 └── TaskIQ worker (Redis broker) -> process_incoming_order
```

## Running With Docker

1. Create a `.env` file (values below mirror container defaults but feel free to override):

    ```dotenv
    REDIS_DSN=redis://redis:6379/0
    BROKER_URL=kafka:9092
    DB_USER=order_service_user
    DB_PASSWORD=order_service
    DB_HOST=db
    DB_PORT=5432
    DB_NAME=order_service
    JWT_SECRET_KEY=change-me
    JWT_HASHING_ALGORITHM=HS256
    JWT_ACCESS_TOKEN_EXPIRATION_MINUTES=30
    JWT_REFRESH_TOKEN_EXPIRATION_MINUTES=80
    LOGGING_LVL=INFO
    LOGGING_FMT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
    SLOWAPI_RATELIMIT=30/minute
    SERVING_PORT=8000
    CORS_ALLOW_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
    CORS_ALLOW_HEADERS=["Authorization","Content-Type"]
    CORS_ALLOW_METHODS=["GET","POST"]
    CORS_ALLOW_CREDENTIALS=true
    ```

2. Build and start the stack:

    ```bash
    docker compose up --build
    ```

    This brings up PostgreSQL, Redis, Zookeeper, Kafka, the FastAPI service, and the Kafka worker. The API exposes `http://localhost:${SERVING_PORT:-8000}`; Swagger UI is available at `/docs`.

3. Observe service health:
   - API: `curl -f http://localhost:${SERVING_PORT:-8000}/docs` (should return 200).
   - Worker: Docker health check hits `http://localhost:8010/internal/alive`; logs show `Order <id> processed` for each event.

## Environment Variables

| Variable | Description | Default in Docker |
| --- | --- | --- |
| `REDIS_DSN` | Redis connection string used by the API. | `redis://redis:6379/0` |
| `BROKER_URL` | Kafka bootstrap servers. | `kafka:9092` |
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` | PostgreSQL credentials. | `order_service_user`, `order_service`, `db`, `5432`, `order_service` |
| `DB_DRIVER` | Async SQLAlchemy driver. | `postgresql+asyncpg` |
| `DB_SYNC_DRIVER` | Driver used by Alembic. | `postgresql+psycopg2` |
| `JWT_SECRET_KEY` | Secret key for signing tokens. | _required_ |
| `JWT_HASHING_ALGORITHM` | Algorithm passed to PyJWT. | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRATION_MINUTES` | Access token TTL. | `30` |
| `JWT_REFRESH_TOKEN_EXPIRATION_MINUTES` | Refresh token TTL. | `80` |
| `LOGGING_LVL` | Python logging level. | `INFO` |
| `LOGGING_FMT` | Logging formatter. | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` |
| `SLOWAPI_RATELIMIT` | Default rate limit. | `30/minute` |
| `SERVING_PORT` | Host port for the API container. | `8000` |

## Database & Migrations

Alembic migrations live under `src/alembic`. Use the pre-installed `uv` CLI inside the API container:

## API Quick Reference

- `POST /register` – Register a new user (`{"email": ..., "password": ...}`).
- `POST /auth/token` – Exchange email/password for access and refresh tokens (OAuth2 password grant using form data).
- `GET /orders/user/{user_id}` – Paginate another user’s orders (admin use cases) via `page` and `page_size` query params.
- `POST /orders` – Create an order for the authenticated caller (`items` is arbitrary JSON) and emit a Kafka event.
- `GET /orders/{order_id}` – Fetch an order; hits Redis cache first, Postgres otherwise.
- `PATCH /orders/{order_id}` – Update order status when you are the creator.

The OpenAPI spec lives at `/docs` and `/openapi.json` once the container is running.

## Kafka Consumer

`src/order_consumer` is bundled into the `worker` service. It subscribes to `new_order` and enqueues TaskIQ jobs (Redis-backed) that simulate downstream work:

```python
@router.subscriber("new_order")
async def process_incoming_order(incoming_order: IncomingOrder) -> None:
    await asyncio.sleep(2)
    print(f"Order {incoming_order.id} processed")
```

Docker keeps it healthy via the `/internal/alive` ASGI endpoint (`uvicorn` on port `8010`).

## Project Layout

```
src/
├── order_service/         # FastAPI application
│   ├── routers/           # Auth + order endpoints
│   ├── services/          # Domain logic
│   ├── repos/             # SQLAlchemy + Redis repositories
│   ├── models/            # SQLAlchemy models
│   ├── dto/, schemas/     # Pydantic request/response layers
│   └── app.py             # FastAPI factory & lifespan hooks
├── order_consumer/        # FastStream Kafka consumer
├── order_worker/          # TaskIQ Redis worker
└── alembic/               # Database migrations
```

## Troubleshooting

- **Kafka not ready** – compose waits for health checks; confirm ports `9092`/`2181` are free.
- **JWT errors** – ensure every API replica shares the same `JWT_SECRET_KEY`.
- **Redis timeouts** – restart the Redis container or adjust `REDIS_DSN` if you mapped a different host/port.
- **Migrations failing** – rerun `docker compose exec api uv run alembic upgrade head` after the database is reachable.

## License

Distributed under the terms of the [MIT License](LICENSE).
