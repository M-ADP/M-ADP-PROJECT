from enum import Enum

from src.core.client.http import HttpClient
from src.core.client.project_monitoring import ProjectMonitoringClient, UniqueUsersData
from src.core.exceptions import MonitoringServerException
from src.common.config.monitoring_server import MonitoringServerConfig
from src.infra.client.asyncio_http import AioHttpClient


class MonitoringAPIUrls(str, Enum):
    GET_UNIQUE_USERS = "/monitoring/project/{project_id}/users"


class MonitoringClientImpl(ProjectMonitoringClient):

    def __init__(
        self,
        monitoring_server_config: MonitoringServerConfig,
        http_client: HttpClient = AioHttpClient(),
    ):
        self.base_url = monitoring_server_config.SERVER_BASE_URL
        self.http_client = http_client

    async def get_unique_users(self, project_id: str) -> UniqueUsersData:
        try:
            response = await self.http_client.get(
                self.base_url + MonitoringAPIUrls.GET_UNIQUE_USERS.format(
                    project_id=project_id
                ),
            )
        except Exception as e:
            raise MonitoringServerException() from e

        try:
            if response.status != 200:
                raise MonitoringServerException(
                    f"모니터링 서버 응답 오류: {response.status}"
                )
            payload = await response.json(content_type=None)
            data = payload.get("data", payload)
            return UniqueUsersData(
                dau=data["dau"],
                wau=data["wau"],
                mau=data["mau"],
            )
        except MonitoringServerException:
            raise
        except Exception as e:
            raise MonitoringServerException() from e
        finally:
            response.release()
