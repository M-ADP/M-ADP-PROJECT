from enum import Enum

from src.common.config.application_server import ApplicationServerConfig
from src.core.client.application import ApplicationClient, ApplicationItemData, DeploymentSummaryItem
from src.core.client.http import HttpClient
from src.infra.client.asyncio_http import AioHttpClient


class ApplicationAPIUrls(str, Enum):
    LIST_BY_PROJECT = "/application/projects/{project_id}/apps"
    GET_SUMMARY_BATCH = "/application/projects/summary"


class ApplicationClientImpl(ApplicationClient):
    """앱 배포 정보 HTTP 클라이언트"""

    def __init__(
        self,
        config: ApplicationServerConfig,
        http_client: HttpClient | None = None,
    ):
        self.http_client = http_client or AioHttpClient(base_url=config.SERVER_BASE_URL)

    async def list_by_project(
        self,
        project_id: int,
    ) -> list[ApplicationItemData]:
        response = await self.http_client.get(
            ApplicationAPIUrls.LIST_BY_PROJECT.format(project_id=project_id),
        )
        try:
            if response.status != 200:
                return []

            payload = await response.json(content_type=None)
            return [
                ApplicationItemData(
                    id=item["id"],
                    name=item["name"],
                    runtime=item.get("runtime"),
                    pod_count=item.get("pod_count", 0),
                    exposed_port=item.get("exposed_port"),
                    cpu_usage_percent=item.get("cpu_usage_percent"),
                    ram_usage_percent=item.get("ram_usage_percent"),
                    health_status=item.get("health_status", "Stopped"),
                )
                for item in payload
            ]
        except Exception:
            return []
        finally:
            response.release()

    async def get_summary_batch(
        self,
        project_ids: list[int],
    ) -> list[DeploymentSummaryItem]:
        response = await self.http_client.post(
            ApplicationAPIUrls.GET_SUMMARY_BATCH,
            json={"project_ids": project_ids},
        )
        try:
            if response.status != 200:
                return []

            payload = await response.json(content_type=None)
            return [
                DeploymentSummaryItem(
                    project_id=item["project_id"],
                    running=item.get("running", 0),
                    warning=item.get("warning", 0),
                    state=item.get("state", "STOPPED"),
                )
                for item in payload
            ]
        except Exception:
            return []
        finally:
            response.release()
