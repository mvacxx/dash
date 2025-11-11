from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field("Marketing Insights Dashboard", env="APP_NAME")
    database_url: str = Field(
        "sqlite+aiosqlite:///./app.db", env="DATABASE_URL"
    )
    facebook_api_version: str = Field("v18.0", env="FACEBOOK_API_VERSION")
    secret_key: str = Field("super-secret-key", env="SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    scheduler_daily_hour_utc: int = Field(3, ge=0, le=23, env="SCHEDULER_DAILY_HOUR_UTC")
    scheduler_daily_minute_utc: int = Field(15, ge=0, le=59, env="SCHEDULER_DAILY_MINUTE_UTC")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
