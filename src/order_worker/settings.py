from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_dsn: str = "redis://redis:6379/0"


settings = Settings()
