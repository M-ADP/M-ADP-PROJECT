import logging
from enum import Enum

from src.core.domain.project import Project
from src.core.client.http import HttpClient
from src.core.client.project_resource import (
    ProjectResourceClient,
    ProjectResourceSnapshotData,
    ResourceMetricSnapshotData,
    ResourceSnapshotData,
)
from src.core.exceptions import ResourceServerException
from src.common.config.resource_server import ResourceServerConfig
from src.infra.client.asyncio_http import AioHttpClient
from src.infra.client.schemas import (
    ExternalProjectCreate,
    ExternalResourceUpdate,
)

logger = logging.getLogger(__name__)


class ProjectResourceAPIUrls(str, Enum):
    CREATE_PROJECT = "/projects"
    DELETE_PROJECT = "/projects/{project_id}"
    GET_PROJECT_RESOURCES = "/projects/{project_id}/resource"
    UPDATE_PROJECT_RESOURCES = "/projects/{project_id}/resource"


class ProjectResourceClientImpl(ProjectResourceClient):

    def __init__(
            self,
            resource_server_config : ResourceServerConfig,
            http_client: HttpClient = AioHttpClient(),
    ):
        self.base_url = resource_server_config.SERVER_BASE_URL
        self.http_client = http_client

    async def _request(
        self,
        coro,
        *,
        operation: str,
        project_id: int,
        url: str,
    ) -> None:
        try:
            response = await coro
        except Exception as e:
            logger.error(f"리소스 서버 연결 실패: {self.base_url}, error: {e}")
            raise ResourceServerException() from e

        try:
            status = getattr(response, "status", None)
            ok = getattr(response, "ok", status is not None and 200 <= status < 400)
            if not ok:
                logger.error(f"리소스 서버 응답 오류: {self.base_url}, status: {status}")
                raise ResourceServerException(
                    f"리소스 서버 응답 오류: {status}"
                )
        finally:
            if hasattr(response, "release"):
                response.release()

    def _convert_cpu(self, val: float | None) -> str | None:
        if val is None:
            return None
        return f"{int(val * 1000)}m"

    def _convert_memory(self, val: float | None) -> str | None:
        if val is None:
            return None
        return f"{int(val * 1024)}Mi"

    async def create(self, user_id: int, role: str, project: Project) -> None:
        payload = ExternalProjectCreate(
            id=str(project.id),
            name=str(project.id),
            cpu=self._convert_cpu(project.max_cpu),
            memory=self._convert_memory(project.max_memory),
            disk=self._convert_memory(project.max_disk),
        )
        url = self.base_url + ProjectResourceAPIUrls.CREATE_PROJECT
        logger.info(
            "[ProjectResourceClient] create 요청: project_id=%s, user_id=%s, role=%s, url=%s, payload=%s",
            project.id,
            user_id,
            role,
            url,
            payload.model_dump(exclude_none=True),
        )
        await self._request(
            self.http_client.post(
                url,
                headers={"X-User-Id": str(user_id), "X-User-Role": role},
                json=payload.model_dump(exclude_none=True),
            ),
            operation="create",
            project_id=project.id,
            url=url,
        )

    async def delete(self, user_id: int, role: str, project: Project) -> None:
        url = self.base_url + ProjectResourceAPIUrls.DELETE_PROJECT.format(
            project_id=project.id
        )
        logger.info(
            "[ProjectResourceClient] delete 요청: project_id=%s, user_id=%s, role=%s, url=%s",
            project.id,
            user_id,
            role,
            url,
        )
        await self._request(
            self.http_client.delete(
                url,
                headers={"X-User-Id": str(user_id), "X-User-Role": role},
            ),
            operation="delete",
            project_id=project.id,
            url=url,
        )

    async def allocate(self, user_id: int, role: str, project: Project) -> None:
        payload = ExternalResourceUpdate(
            cpu=self._convert_cpu(project.max_cpu),
            memory=self._convert_memory(project.max_memory),
            disk=self._convert_memory(project.max_disk),
        )
        url = self.base_url + ProjectResourceAPIUrls.UPDATE_PROJECT_RESOURCES.format(
            project_id=project.id
        )
        logger.info(
            "[ProjectResourceClient] allocate 요청: project_id=%s, user_id=%s, role=%s, url=%s, payload=%s",
            project.id,
            user_id,
            role,
            url,
            payload.model_dump(exclude_none=True),
        )
        await self._request(
            self.http_client.patch(
                url,
                headers={"X-User-Id": str(user_id), "X-User-Role": role},
                json=payload.model_dump(exclude_none=True),
            ),
            operation="allocate",
            project_id=project.id,
            url=url,
        )

    async def get_usage(
        self,
        project: Project,
        days: int = 7,
        interval_minutes: int = 60,
    ) -> ProjectResourceSnapshotData:
        url = self.base_url + ProjectResourceAPIUrls.GET_PROJECT_RESOURCES.format(
            project_id=project.id
        )
        logger.info(
            "[ProjectResourceClient] get_usage 요청: project_id=%s, url=%s",
            project.id,
            url,
        )
        try:
            response = await self.http_client.get(url)
        except Exception as e:
            logger.error(f"리소스 서버 연결 실패: {self.base_url}, error: {e}")
            raise ResourceServerException() from e

        try:
            logger.info(
                "[ProjectResourceClient] get_usage 응답: status=%s, project_id=%s, url=%s",
                response.status,
                project.id,
                url,
            )
            if response.status != 200:
                logger.error(f"리소스 서버 응답 오류: {self.base_url}, status: {response.status}")
                raise ResourceServerException(
                    f"리소스 서버 응답 오류: {response.status}"
                )
            payload = await response.json(content_type=None)
            data = payload.get("data", payload)
            logger.debug(
                "[ProjectResourceClient] get_usage 파싱: project_id=%s, payload_keys=%s",
                project.id,
                list(data.keys()) if isinstance(data, dict) else None,
            )
            return ProjectResourceSnapshotData(
                project_id=str(data["project_id"]),
                cpu=ResourceMetricSnapshotData(
                    limit=data["cpu"]["limit"],
                    used=data["cpu"]["used"],
                    percentage=data["cpu"]["percentage"],
                    unit=data["cpu"]["unit"],
                ),
                memory=ResourceMetricSnapshotData(
                    limit=data["memory"]["limit"],
                    used=data["memory"]["used"],
                    percentage=data["memory"]["percentage"],
                    unit=data["memory"]["unit"],
                ),
                disk=ResourceMetricSnapshotData(
                    limit=data["disk"]["limit"],
                    used=data["disk"]["used"],
                    percentage=data["disk"]["percentage"],
                    unit=data["disk"]["unit"],
                ),
                instance=ResourceSnapshotData(
                    limit=data["instance"]["limit"],
                    used=data["instance"]["used"],
                    percentage=data["instance"]["percentage"],
                ),
            )
        except ResourceServerException:
            raise
        except Exception as e:
            logger.error(f"리소스 서버 응답 처리 오류: {self.base_url}, error: {e}")
            raise ResourceServerException() from e
        finally:
            response.release()
