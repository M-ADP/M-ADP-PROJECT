from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.common.const.vault import VAULT_ENV_FILE


class ResourceServerConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RESOURCE_",
        extra="ignore",
        env_file=VAULT_ENV_FILE,
        env_file_encoding="utf-8",
    )

    SERVER_BASE_URL: str = "http://localhost:8001"
    # env에 이거 추가하면 됨
    # ex) SERVER_BASE_URL=https:// ···

@lru_cache
def get_resource_config() -> ResourceServerConfig:
    return ResourceServerConfig()