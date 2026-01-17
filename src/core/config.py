from functools import lru_cache
from typing import List

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class CorsSettings(BaseModel):
    allow_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    allow_methods: List[str] = ["*"]
    allow_credentials: bool = True
    allow_headers: List[str] = ["*"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MADP_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app_name: str = "MADP Project Service"
    app_version: str = "v1"
    cors: CorsSettings = CorsSettings()

class ProjectConfig:
    LIMIT : int = 3
    DNS_DOMAIN : str = "mdeveloper.platform"


@lru_cache
def get_settings() -> Settings:
    return Settings()
