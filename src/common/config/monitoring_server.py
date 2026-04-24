from functools import lru_cache

from pydantic_settings import SettingsConfigDict

from src.common.config.settings import LoggedSettings, register_config
from src.common.const.vault import VAULT_ENV_FILE


class MonitoringServerConfig(LoggedSettings):
    model_config = SettingsConfigDict(
        env_prefix="MONITORING_",
        extra="ignore",
        env_file=VAULT_ENV_FILE,
        env_file_encoding="utf-8",
    )

    SERVER_BASE_URL: str = "http://localhost:8005"


@register_config
@lru_cache
def get_monitoring_config() -> MonitoringServerConfig:
    return MonitoringServerConfig()
