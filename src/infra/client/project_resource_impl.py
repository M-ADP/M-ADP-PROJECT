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

    async def _request(self, coro) -> None:
        try:
            response = await coro
        except Exception as e:
            raise ResourceServerException() from e
        if not response.ok:
            raise ResourceServerException(
                f"리소스 서버 응답 오류: {response.status}"
            )

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
        await self._request(self.http_client.post(
            self.base_url + ProjectResourceAPIUrls.CREATE_PROJECT,
            headers={"X-User-Id": str(user_id), "X-User-Role": role},
            json=payload.model_dump(exclude_none=True),
        ))

    async def delete(self, user_id: int, role: str, project: Project) -> None:
        await self._request(self.http_client.delete(
            self.base_url + ProjectResourceAPIUrls.DELETE_PROJECT.format(
                project_id=project.id
            ),
            headers={"X-User-Id": str(user_id), "X-User-Role": role},
        ))

    async def allocate(self, user_id: int, role: str, project: Project) -> None:
        payload = ExternalResourceUpdate(
            cpu=self._convert_cpu(project.max_cpu),
            memory=self._convert_memory(project.max_memory),
            disk=self._convert_memory(project.max_disk),
        )
        await self._request(self.http_client.patch(
            self.base_url + ProjectResourceAPIUrls.UPDATE_PROJECT_RESOURCES.format(
                project_id=project.id
            ),
            headers={"X-User-Id": str(user_id), "X-User-Role": role},
            json=payload.model_dump(exclude_none=True),
        ))

    async def get_usage(
        self,
        project: Project,
        user_id: int,
        days: int = 7,
        interval_minutes: int = 60,
    ) -> ProjectResourceSnapshotData:
        try:
            response = await self.http_client.get(
                self.base_url + ProjectResourceAPIUrls.GET_PROJECT_RESOURCES.format(
                    project_id=project.id
                ),
                headers={"X-User-Id": str(user_id)},
            )
        except Exception as e:
            raise ResourceServerException() from e

        try:
            if response.status != 200:
                raise ResourceServerException(
                    f"리소스 서버 응답 오류: {response.status}"
                )
            payload = await response.json(content_type=None)
            data = payload.get("data", payload)
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
            raise ResourceServerException() from e
        finally:
            response.release()
