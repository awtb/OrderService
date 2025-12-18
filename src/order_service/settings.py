from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    pg_user: str
    pg_password: str
    pg_host: str
    pg_port: str
    pg_db: str
