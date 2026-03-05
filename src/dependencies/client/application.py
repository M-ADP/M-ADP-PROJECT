from fastapi import Depends

from src.core.client.application import ApplicationClient
from src.common.config.application_server import get_application_server_config
from src.dependencies.auth import UserInfo, get_user_info
from src.infra.client import ApplicationClientImpl
from src.infra.client.asyncio_http import AioHttpClient


def get_deployment_client(
    user: UserInfo = Depends(get_user_info),
) -> ApplicationClient:
    config = get_application_server_config()
    http_client = AioHttpClient(
        base_url=config.SERVER_BASE_URL,
        headers={"X-User-Id": str(user.user_id), "X-User-Role": user.role},
    )
    return ApplicationClientImpl(config=config, http_client=http_client)
