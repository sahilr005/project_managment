from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    env: str = Field(default='dev',alias="ENV")
    app_name: str = Field(default='pm-saas-backend',alias='APP_NAME')
    host: str = Field(default="127.0.0.1",alias="APP_HOST")
    port: int = Field(default=8000, alias="APP_PORT")

    database_url: str = Field(
        default="postgresql+asyncpg://sahil:1234@localhost:5432/mydb",
        # default="postgresql+asyncpg://postgres:postgres@localhost:5432/pmdb",
        alias="DATABASE_URL"
    )
    redis_url: str = Field(default="redis://localhost:6379/0",alias="REDIS_URL")
    jwt_secret: str = Field(default="change-me-in-prod", alias="JWT_SECRET")

    class Congig:
        env_file = ".env"
        case_sensitive = False
        
settings =Settings()