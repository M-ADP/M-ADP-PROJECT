from src.common.client.project_resource import (
    MockProjectResourceClient,
    ProjectResourceClient,
)
from src.common.config.resource_server import get_resource_config

from src.infra.client import ProjectResourceClientImpl


def get_project_resource_client() -> ProjectResourceClient:
    resource_config = get_resource_config()
    return ProjectResourceClientImpl(
        resource_server_config=resource_config
    )

# 나중에 ProjectResourceClientImpl으로 반환하게 수정하면 됨