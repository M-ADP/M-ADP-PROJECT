from fastapi import Depends

from src.core.client.user import UserClient
from src.common.config.user_server import get_user_server_config
from src.dependencies.auth import UserInfo, get_user_info
from src.infra.client.asyncio_http import AioHttpClient
from src.infra.client.user_impl import UserClientImpl


def get_user_client(user: UserInfo = Depends(get_user_info)) -> UserClient:
    http_client = AioHttpClient(
        headers={"X-User-Id": str(user.user_id), "X-User-Role": user.role}
    )
    return UserClientImpl(user_server_config=get_user_server_config(), http_client=http_client)
