from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field("Marketing Insights Dashboard", env="APP_NAME")
    database_url: str = Field(
        "sqlite+aiosqlite:///./app.db", env="DATABASE_URL"
    )
    facebook_api_version: str = Field("v18.0", env="FACEBOOK_API_VERSION")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
