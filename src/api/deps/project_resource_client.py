from src.common.client.project_resource import (
    MockProjectResourceClient,
    ProjectResourceClient,
)

from src.infra.client import ProjectResourceClientImpl


def get_project_resource_client() -> ProjectResourceClient:
    return ProjectResourceClientImpl()

# 나중에 ProjectResourceClientImpl으로 반환하게 수정하면 됨