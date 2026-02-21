from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class UserServerConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="USER_",
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    SERVER_BASE_URL: str = "http://localhost:8002"


@lru_cache
def get_user_server_config() -> UserServerConfig:
    return UserServerConfig()
