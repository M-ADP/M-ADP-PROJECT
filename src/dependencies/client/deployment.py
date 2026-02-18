from src.core.client.deployment import DeploymentClient
from src.infra.client import MockDeploymentClient


def get_deployment_client() -> DeploymentClient:
    return MockDeploymentClient()
