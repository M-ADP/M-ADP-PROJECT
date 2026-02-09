from src.common.client.project_resource import (
    MockProjectResourceClient,
    ProjectResourceClient,
)


def get_project_resource_client() -> ProjectResourceClient:
    return MockProjectResourceClient()

# 나중에 ProjectResourceClientImpl으로 반환하게 수정하면 됨