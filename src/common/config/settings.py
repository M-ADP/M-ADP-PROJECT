import logging
from functools import lru_cache
from typing import Any, Callable, List
from urllib.parse import quote_plus

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.common.const.vault import VAULT_ENV_FILE

logger = logging.getLogger(__name__)

_CONFIG_GETTERS: list[Callable] = []


def register_config(fn: Callable) -> Callable:
    _CONFIG_GETTERS.append(fn)
    return fn


def load_all_configs() -> None:
    for getter in _CONFIG_GETTERS:
        getter()


class LoggedSettings(BaseSettings):
    def model_post_init(self, __context: Any) -> None:
        prefix = self.model_config.get("env_prefix", "").upper()
        fields_info = {
            f"{prefix}{name.upper()}": getattr(self, name)
            for name in self.model_fields
        }
        logger.info("[Config Loaded] %s → %s", self.__class__.__name__, fields_info)


class CorsSettings(BaseModel):
    allow_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    allow_methods: List[str] = ["*"]
    allow_credentials: bool = True
    allow_headers: List[str] = ["*"]


class AppConfig(LoggedSettings):
    model_config = SettingsConfigDict(
        env_prefix="MADP_",
        env_file=VAULT_ENV_FILE,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app_name: str = "MADP Project Service"
    app_version: str = "0.0.1"
    cors: CorsSettings = CorsSettings()


class DatabaseConfig(LoggedSettings):
    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=VAULT_ENV_FILE,
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
        return f"mysql+aiomysql://{quote_plus(self.user)}:{quote_plus(self.password)}@{self.host}:{self.port}/{self.name}"


class SonyflakeConfig(LoggedSettings):
    model_config = SettingsConfigDict(
        env_prefix="SONYFLAKE_",
        env_file=VAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    machine_id: int = 0


class ProjectConfig:
    LIMIT: int = 3


@register_config
@lru_cache
def get_app_config() -> AppConfig:
    return AppConfig()


@register_config
@lru_cache
def get_db_config() -> DatabaseConfig:
    return DatabaseConfig()


@register_config
@lru_cache
def get_sonyflake_config() -> SonyflakeConfig:
    return SonyflakeConfig()
