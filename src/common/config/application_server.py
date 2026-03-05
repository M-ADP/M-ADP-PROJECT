from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.common.const.vault import VAULT_ENV_FILE


class ApplicationServerConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APPLICATION_",
        extra="ignore",
        env_file=VAULT_ENV_FILE,
        env_file_encoding="utf-8",
    )

    SERVER_BASE_URL: str = "http://localhost:8003"


@lru_cache
def get_application_server_config() -> ApplicationServerConfig:
    return ApplicationServerConfig()
