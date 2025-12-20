# Order Service

Asynchronous FastAPI service for managing customer orders. It exposes a REST API for registering users, issuing JWT token pairs, creating and tracking orders, and publishing every new order into Kafka so that downstream consumers can pick them up. Redis is used to cache hot orders, PostgreSQL stores the source of truth, and a small FastStream-based worker processes the Kafka events.

## Architecture At A Glance

- **API** – `order_service`, a FastAPI app configured via Typer (`python -m order_service`) with SlowAPI rate limiting, JWT auth and Alembic migrations.
- **Database** – PostgreSQL accessed with SQLAlchemy 2.0 async sessions plus Redis for caching `Order` rows by id.
- **Messaging** – Kafka broker. The API publishes a `new_order` event after every successful `POST /orders` call.
- **Consumer** – `order_consumer` (FastStream + uvicorn) receives those Kafka messages and simulates downstream processing.
- **Infrastructure** – Dockerfile installs Python 3.14 with [uv](https://github.com/astral-sh/uv); `compose.yaml` starts postgres, redis, kafka, zookeeper, API, and consumer.

```
FastAPI (Orders, Auth)
 ├── PostgreSQL (orders, users)
 ├── Redis cache (order:<id>)
 ├── KafkaBroker (topic=new_order)
 └── SlowAPI rate limiting

FastStream consumer
 └── Kafka subscriber -> process_incoming_order
```

## Key Features

- OAuth2 password flow with hashed credentials (bcrypt) and signed JWT access/refresh tokens.
- Async SQLAlchemy repositories with typed DTOs and pagination helpers.
- Redis-backed read-through cache for `GET /orders/{id}` and automatic invalidation on writes.
- Kafka integration using FastStream; every new order is published to the `new_order` topic.
- Separate Kafka consumer service with health endpoint for Docker health checks.
- SlowAPI rate limiting (default `30/minute`) and structured logging.

## Tech Stack

FastAPI · Typer · FastStream · Kafka · PostgreSQL · SQLAlchemy 2.0 · Alembic · Redis · bcrypt · PyJWT · uv

## Local Development

### Requirements

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) (preferred) or another PEP 517 installer
- Docker (optional but recommended for dependencies)


### 1. Configure environment

Create a `.env` at the repo root (everything below matches `Settings` defaults and `.env` is auto-loaded):

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
```

### 2. Start backing services

Either bring up the full stack (recommended):

```bash
docker compose up -d db redis zookeeper kafka
```

or point the env vars to already running services.

### 3. Run database migrations

```bash
uv run alembic upgrade head
```

### 5. Start the API (FastAPI + Swagger)

```bash
uv run python -m order_service --reload
# http://localhost:8000/docs shows the interactive docs
```

### 5. Start the Kafka consumer (optional but useful when testing events)

```bash
uv run python -m order_consumer
```

> Convenience: `scripts/dev.sh` runs migrations and the API; `scripts/start-consumer.sh` launches the consumer. Both expect `PYTHONPATH=$(pwd)/src` which the scripts export automatically.

## Docker Compose Deployment

`compose.yaml` wires the API service, consumer, postgres, redis, kafka, and zookeeper. Build and start everything with:

```bash
docker compose up --build
```

Key notes:

- API container runs `scripts/prod.sh` (no reload) and exposes `${SERVING_PORT:-8000}`.
- Worker container runs `scripts/start-consumer.sh` with a health check on `http://localhost:8010/internal/alive`.
- Provide the same configuration variables via your `.env` or compose overrides before running the stack.

## Environment Variables

| Variable | Description | Default |
| --- | --- | --- |
| `REDIS_DSN` | Redis connection string for caching orders. | `redis://redis:6379/0` (container) |
| `BROKER_URL` | Kafka bootstrap servers. | `kafka:9092` |
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` | PostgreSQL connection parameters. | — |
| `DB_DRIVER` | Async SQLAlchemy driver. | `postgresql+asyncpg` |
| `DB_SYNC_DRIVER` | Synchronous driver (used by Alembic). | `postgresql+psycopg2` |
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens. | — |
| `JWT_HASHING_ALGORITHM` | Algorithm used by PyJWT. | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRATION_MINUTES` | Access token TTL. | `30` |
| `JWT_REFRESH_TOKEN_EXPIRATION_MINUTES` | Refresh token TTL. | `80` |
| `LOGGING_LVL` | Python logging level. | `INFO` |
| `LOGGING_FMT` | Logging format string. | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` |
| `SLOWAPI_RATELIMIT` | Rate limit applied by SlowAPI. | `30/minute` |

## Database & Migrations

Alembic lives under `src/alembic`. Two migrations ship with the repo:

1. `c99c45f5e094_add_users_table.py`
2. `69e23a157c0b_add_orders_table.py`

Use standard Alembic commands (run via `uv run` so the virtualenv + `PYTHONPATH` are configured):

```bash
uv run alembic revision -m "short description"
uv run alembic upgrade head
uv run alembic downgrade -1
```

## API Quick Reference

Authentication endpoints (no prefix):

- `POST /register` – create a user. Body: `{ "email": "user@example.com", "password": "..." }`.
- `POST /auth/token` – OAuth2 password flow. Pass credentials via form data; returns access + refresh tokens.

Orders (`/orders` prefix, bearer token required except the user listing):

- `GET /orders/user/{user_id}?page=1&page_size=10` – paginate a user’s orders (helpful for admin/use cases).
- `POST /orders` – create an order for the authenticated user. Body is an arbitrary JSON `items` object.
- `GET /orders/{order_id}` – fetch a single order. Reads from Redis cache when warm, falls back to Postgres.
- `PATCH /orders/{order_id}` – update the order status (owner only).

OpenAPI docs live at `/docs` once the API is up.

## Kafka Consumer

`src/order_consumer` is a FastStream application that subscribes to the `new_order` topic and simulates work:

```python
@router.subscriber("new_order")
async def process_incoming_order(incoming_order: IncomingOrder) -> None:
    await asyncio.sleep(2)
    print(f"Order {incoming_order.id} processed")
```

Run it locally with `uv run python -m order_consumer` or rely on the `worker` service in Docker Compose.

## Project Layout

```
src/
├── order_service/         # FastAPI app
│   ├── routers/           # Auth + order endpoints
│   ├── services/          # Domain logic (auth, order)
│   ├── repos/             # SQLAlchemy repositories + Redis cache helpers
│   ├── models/            # SQLAlchemy models (users, orders)
│   ├── dto/, schemas/     # Pydantic request/response and DTOs
│   └── app.py             # FastAPI factory with Redis/Kafka/Postgres setup
├── order_consumer/        # FastStream Kafka consumer
└── alembic/               # Database migrations
```

## Troubleshooting

- **Kafka not ready** – compose waits for health checks; make sure ports `9092/2181` are free.
- **JWT errors** – confirm `JWT_SECRET_KEY` matches between API instances; tokens break if rotated without logout.
- **Redis connection timeouts** – adjust `REDIS_DSN` or run `docker compose restart redis` if local setup changed.

## License

This project is distributed under the terms of the [MIT License](LICENSE).
