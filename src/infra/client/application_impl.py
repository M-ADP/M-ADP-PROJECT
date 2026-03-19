import logging
from enum import Enum

from src.common.config.application_server import ApplicationServerConfig
from src.core.client.application import ApplicationClient, ApplicationItemData, DeploymentSummaryItem
from src.core.client.http import HttpClient
from src.infra.client.asyncio_http import AioHttpClient

logger = logging.getLogger(__name__)


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
        user_id: int,
        role: str,
    ) -> list[ApplicationItemData]:
        url = ApplicationAPIUrls.LIST_BY_PROJECT.format(project_id=project_id)
        logger.info(
            "[ApplicationClient] list_by_project 요청: project_id=%s, user_id=%s, role=%s, url=%s",
            project_id, user_id, role, url,
        )
        response = await self.http_client.get(
            url,
            headers={"X-User-Id": str(user_id), "X-User-Role": role},
        )
        try:
            logger.info(
                "[ApplicationClient] list_by_project 응답: status=%s, project_id=%s",
                response.status, project_id,
            )
            if response.status != 200:
                body = await response.text()
                logger.warning(
                    "[ApplicationClient] list_by_project 비정상 응답: status=%s, body=%s",
                    response.status, body[:500],
                )
                return []

            payload = await response.json(content_type=None)
            items = payload.get("data", []) if isinstance(payload, dict) else payload
            logger.debug(
                "[ApplicationClient] list_by_project 파싱: items_count=%s, project_id=%s",
                len(items), project_id,
            )
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
                for item in items
            ]
        except Exception:
            logger.exception(
                "[ApplicationClient] list_by_project 예외 발생: project_id=%s",
                project_id,
            )
            return []
        finally:
            response.release()

    async def get_summary_batch(
        self,
        project_ids: list[int],
        user_id: int,
        role: str,
    ) -> list[DeploymentSummaryItem]:
        logger.info(
            "[ApplicationClient] get_summary_batch 요청: project_ids=%s, user_id=%s, role=%s",
            project_ids, user_id, role,
        )
        response = await self.http_client.post(
            ApplicationAPIUrls.GET_SUMMARY_BATCH,
            json={"project_ids": project_ids},
            headers={"X-User-Id": str(user_id), "X-User-Role": role},
        )
        try:
            logger.info(
                "[ApplicationClient] get_summary_batch 응답: status=%s, project_ids=%s",
                response.status, project_ids,
            )
            if response.status != 200:
                body = await response.text()
                logger.warning(
                    "[ApplicationClient] get_summary_batch 비정상 응답: status=%s, body=%s",
                    response.status, body[:500],
                )
                return []

            payload = await response.json(content_type=None)
            items = payload.get("data", []) if isinstance(payload, dict) else payload
            logger.debug(
                "[ApplicationClient] get_summary_batch 파싱: items_count=%s, project_ids=%s",
                len(items), project_ids,
            )
            return [
                DeploymentSummaryItem(
                    project_id=item["project_id"],
                    running=item.get("running", 0),
                    warning=item.get("warning", 0),
                    state=item.get("state", "STOPPED"),
                )
                for item in items
            ]
        except Exception:
            logger.exception(
                "[ApplicationClient] get_summary_batch 예외 발생: project_ids=%s",
                project_ids,
            )
            return []
        finally:
            response.release()

