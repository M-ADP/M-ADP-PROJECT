from functools import lru_cache

from src.common.config.settings import LoggedSettings, register_config
from pydantic_settings import SettingsConfigDict

from src.common.const.vault import VAULT_ENV_FILE


class ApplicationServerConfig(LoggedSettings):
    model_config = SettingsConfigDict(
        env_prefix="APPLICATION_",
        extra="ignore",
        env_file=VAULT_ENV_FILE,
        env_file_encoding="utf-8",
    )

    SERVER_BASE_URL: str = "http://localhost:8003"


@register_config
@lru_cache
def get_application_server_config() -> ApplicationServerConfig:
    return ApplicationServerConfig()
