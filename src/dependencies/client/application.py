import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.client.application import ApplicationClient
from src.common.const.vault import VAULT_ENV_FILE


class _FakeConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=VAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )
    use_fake_application_client: bool = False


@lru_cache
def _get_fake_config() -> _FakeConfig:
    return _FakeConfig()


def get_deployment_client() -> ApplicationClient:
    if _get_fake_config().use_fake_application_client:
        from src.infra.client import FakeApplicationClientImpl
        return FakeApplicationClientImpl()
    from src.common.config.application_server import get_application_server_config
    from src.infra.client import ApplicationClientImpl
    return ApplicationClientImpl(config=get_application_server_config())
