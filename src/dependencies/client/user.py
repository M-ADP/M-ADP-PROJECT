from fastapi import Depends

from src.core.client.user import UserClient
from src.common.config.user_server import get_user_server_config
from src.infra.client.user_impl import UserClientImpl
from src.infra.client.asyncio_http import AioHttpClient
from src.dependencies.auth import get_user_info, UserInfo


def get_user_client(user: UserInfo = Depends(get_user_info)) -> UserClient:
    config = get_user_server_config()
    http_client = AioHttpClient(
        base_url=config.SERVER_BASE_URL,
        headers={"X-User-Id": str(user.user_id), "X-User-Role": user.role},
    )
    return UserClientImpl(user_server_config=config, http_client=http_client)
