from src.core.client.application import ApplicationClient


def get_deployment_client() -> ApplicationClient:
    from src.common.config.application_server import get_application_server_config
    from src.infra.client import ApplicationClientImpl
    return ApplicationClientImpl(config=get_application_server_config())
