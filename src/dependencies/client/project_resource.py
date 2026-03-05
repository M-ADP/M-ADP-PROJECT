from fastapi import Depends

from src.core.client.project_resource import ProjectResourceClient
from src.common.config.resource_server import get_resource_config
from src.dependencies.auth import UserInfo, get_user_info
from src.infra.client import ProjectResourceClientImpl
from src.infra.client.asyncio_http import AioHttpClient


def get_project_resource_client(
    user: UserInfo = Depends(get_user_info),
) -> ProjectResourceClient:
    resource_config = get_resource_config()
    http_client = AioHttpClient(
        headers={"X-User-Id": str(user.user_id), "X-User-Role": user.role}
    )
    return ProjectResourceClientImpl(
        resource_server_config=resource_config,
        http_client=http_client,
    )
