from src.core.client.application import ApplicationClient
from src.infra.client import MockApplicationClient


def get_deployment_client() -> ApplicationClient:
    return MockApplicationClient()
