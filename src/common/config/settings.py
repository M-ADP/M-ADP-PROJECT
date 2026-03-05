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


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MADP_",
        env_file="/vault/secrets/.env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app_name: str = "MADP Project Service"
    app_version: str = "0.0.1"
    cors: CorsSettings = CorsSettings()


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file="/vault/secrets/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    user: str = "root"
    password: str = ""
    host: str = "localhost"
    port: str = "3306"
    name: str = "madp"

    @property
    def url(self) -> str:
        return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class SonyflakeConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SONYFLAKE_",
        env_file="/vault/secrets/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    machine_id: int = 0


class ProjectConfig:
    LIMIT: int = 3
    DNS_DOMAIN: str = "mdeveloper.platform"


@lru_cache
def get_app_config() -> AppConfig:
    return AppConfig()


@lru_cache
def get_db_config() -> DatabaseConfig:
    return DatabaseConfig()


@lru_cache
def get_sonyflake_config() -> SonyflakeConfig:
    return SonyflakeConfig()
