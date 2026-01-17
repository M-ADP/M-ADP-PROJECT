from src.common.client.project_resource import ProjectResourceClient
from src.infra.client import MockProjectResourceClient


def get_project_resource_client() -> ProjectResourceClient:
    return MockProjectResourceClient()
