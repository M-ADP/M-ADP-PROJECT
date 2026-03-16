from functools import lru_cache

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.client.user import UserClient
from src.common.const.vault import VAULT_ENV_FILE
from src.dependencies.auth import get_user_info, UserInfo


class _FakeConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=VAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )
    use_fake_user_client: bool = False


@lru_cache
def _get_fake_config() -> _FakeConfig:
    return _FakeConfig()


def get_user_client(user: UserInfo = Depends(get_user_info)) -> UserClient:
    if _get_fake_config().use_fake_user_client:
        from src.infra.client import FakeUserClientImpl
        return FakeUserClientImpl()
    from src.common.config.user_server import get_user_server_config
    from src.infra.client import UserClientImpl
    from src.infra.client.asyncio_http import AioHttpClient
    config = get_user_server_config()
    http_client = AioHttpClient(
        base_url=config.SERVER_BASE_URL,
        headers={"X-User-Id": str(user.user_id), "X-User-Role": user.role},
    )
    return UserClientImpl(user_server_config=config, http_client=http_client)
