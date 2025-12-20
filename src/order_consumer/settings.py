from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    broker_url: str = "kafka:9092"


settings = Settings()
