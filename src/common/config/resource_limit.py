from functools import lru_cache

from pydantic_settings import SettingsConfigDict

from src.common.config.settings import LoggedSettings, register_config
from src.common.const.vault import VAULT_ENV_FILE


class ResourceLimitConfig(LoggedSettings):
    model_config = SettingsConfigDict(
        env_prefix="PROJECT_RESOURCE_",
        extra="ignore",
        env_file=VAULT_ENV_FILE,
        env_file_encoding="utf-8",
    )

    max_cpu: float = 4.0
    max_memory: float = 2.0
    max_disk: float = 50.0


@register_config
@lru_cache
def get_resource_limit_config() -> ResourceLimitConfig:
    return ResourceLimitConfig()
