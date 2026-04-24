from src.core.client.project_monitoring import ProjectMonitoringClient
from src.common.config.monitoring_server import get_monitoring_config
from src.infra.client.monitoring_impl import MonitoringClientImpl


def get_monitoring_client() -> ProjectMonitoringClient:
    return MonitoringClientImpl(monitoring_server_config=get_monitoring_config())
