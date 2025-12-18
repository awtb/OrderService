from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    pg_user: str
    pg_password: str
    pg_host: str
    pg_port: str
    pg_db: str

    jwt_secret_key: str
    jwt_hashing_algorithm: str
    jwt_access_token_expiration_minutes: int = 30
    jwt_refresh_token_expiration_minutes: int = 80

    model_config = SettingsConfigDict(extra="ignore", env_ignore_empty=True)
