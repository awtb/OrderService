from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


def split_csv(value: str) -> list[str]:
    items = [item.strip() for item in value.split(",")]
    return [item for item in items if item]


class Settings(BaseSettings):
    redis_dsn: str = "redis://redis:6379/0"
    broker_url: str = "kafka:9092"

    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_driver: str = "postgresql+asyncpg"
    db_sync_driver: str = "postgresql+psycopg2"

    jwt_secret_key: str
    jwt_hashing_algorithm: str = "HS256"
    jwt_access_token_expiration_minutes: int = 30
    jwt_refresh_token_expiration_minutes: int = 80

    logging_lvl: str = "INFO"
    logging_fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    slowapi_ratelimit: str = "30/minute"
    order_cache_ttl_seconds: int = 300

    cors_allow_origins: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    cors_allow_methods: list[str] = ["*"]
    cors_allow_credentials: bool = True

    model_config = SettingsConfigDict(
        extra="ignore", env_ignore_empty=True, env_file=".env"
    )
