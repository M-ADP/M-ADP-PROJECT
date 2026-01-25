from src.common.client.deployment_summary import DeploymentSummaryClient
from src.infra.client import MockDeploymentSummaryClient


def get_deployment_summary_client() -> DeploymentSummaryClient:
    return MockDeploymentSummaryClient()
