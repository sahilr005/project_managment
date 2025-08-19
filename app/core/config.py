from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Load from project root .env and fallback to app/.env
    model_config = SettingsConfigDict(env_file=(".env", "app/.env"), case_sensitive=False)
    env: str = Field(default='dev',alias="ENV")
    app_name: str = Field(default='pm-saas-backend',alias='APP_NAME')
    host: str = Field(default="127.0.0.1",alias="APP_HOST")
    port: int = Field(default=8000, alias="APP_PORT")

    database_url: str = Field(
        ...,
        # default="postgresql+asyncpg://postgres:postgres@localhost:5432/pmdb",
        alias="DATABASE_URL"
    )
    redis_url: str = Field(default="redis://localhost:6379/0",alias="REDIS_URL")
    jwt_secret: str = Field(default="change-me-in-prod", alias="JWT_SECRET")
    db_ssl_allow_self_signed: bool = Field(default=False, alias="DB_SSL_ALLOW_SELF_SIGNED")
    
settings =Settings()