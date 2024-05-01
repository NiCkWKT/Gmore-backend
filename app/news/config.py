from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION_NAME: str | None = None

    model_config = SettingsConfigDict(env_file=".env")


# Create a cached settings instance
@lru_cache()
def get_settings():
    return Settings()


# Access settings using the cached instance
settings = get_settings()
