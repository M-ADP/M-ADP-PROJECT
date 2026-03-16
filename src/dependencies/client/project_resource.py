from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.client.project_resource import ProjectResourceClient
from src.common.config.resource_server import get_resource_config
from src.common.const.vault import VAULT_ENV_FILE
from src.infra.client import FakeProjectResourceClientImpl, ProjectResourceClientImpl


class _FakeConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=VAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )
    use_fake_resource_client: bool = False


@lru_cache
def _get_fake_config() -> _FakeConfig:
    return _FakeConfig()


def get_project_resource_client() -> ProjectResourceClient:
    if _get_fake_config().use_fake_resource_client:
        return FakeProjectResourceClientImpl()
    return ProjectResourceClientImpl(resource_server_config=get_resource_config())
