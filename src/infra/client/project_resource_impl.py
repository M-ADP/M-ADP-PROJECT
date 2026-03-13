from enum import Enum

from src.core.domain.port import Port
from src.core.domain.project import Project
from src.core.client.http import HttpClient
from src.core.client.project_resource import ProjectResourceClient, ResourceUsageData
from src.core.exceptions import ResourceServerException
from src.common.config.resource_server import ResourceServerConfig
from src.infra.client.asyncio_http import AioHttpClient
from src.infra.client.schemas import (
    ExternalPortCreate,
    ExternalPortUpdate,
    ExternalProjectCreate,
    ExternalResourceUpdate,
)


class ProjectResourceAPIUrls(str, Enum):
    CREATE_PROJECT = "/projects"
    DELETE_PROJECT = "/projects/{project_id}"
    OPEN_PROJECT_PORT = "/projects/{project_id}/ports"
    UPDATE_PROJECT_PORT = "/projects/{project_id}/ports/{port_id}"
    CLOSE_PROJECT_PORT = "/projects/{project_id}/ports/{port_id}"
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

    async def open_port(self, user_id: int, role: str, project: Project, port: Port) -> None:
        payload = ExternalPortCreate(
            service_id=port.service_id,
            service_name=port.service_name,
            target_deployment_name=port.target_deployment_name,
            port=port.port,
            target_port=port.target_port,
            protocol=port.protocol,
            service_type=port.service_type,
        )
        await self._request(self.http_client.post(
            self.base_url + ProjectResourceAPIUrls.OPEN_PROJECT_PORT.format(
                project_id=project.id
            ),
            headers={"X-User-Id": str(user_id), "X-User-Role": role},
            json=payload.model_dump(),
        ))

    async def close_port(self, user_id: int, role: str, project: Project, port: Port) -> None:
        await self._request(self.http_client.delete(
            self.base_url + ProjectResourceAPIUrls.CLOSE_PROJECT_PORT.format(
                project_id=project.id, port_id=port.service_id
            ),
            headers={"X-User-Id": str(user_id), "X-User-Role": role},
        ))

    async def update_port(
        self,
        user_id: int,
        role: str,
        project: Project,
        original_port: Port,
        updated_port: Port,
    ) -> None:
        payload = ExternalPortUpdate(
            service_id=updated_port.service_id,
            service_name=updated_port.service_name,
            target_deployment_name=updated_port.target_deployment_name,
            target_port=updated_port.target_port,
            protocol=updated_port.protocol,
            service_type=updated_port.service_type,
        )
        await self._request(self.http_client.put(
            self.base_url + ProjectResourceAPIUrls.UPDATE_PROJECT_PORT.format(
                project_id=project.id, port_id=original_port.service_id
            ),
            headers={"X-User-Id": str(user_id), "X-User-Role": role},
            json=payload.model_dump(exclude_none=True),
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
        days: int = 7,
        interval_minutes: int = 60,
    ) -> ResourceUsageData:
        print(
            f"프로젝트 {project.id} 최근 {days}일 리소스 사용량 조회 "
            f"(간격 {interval_minutes}분)"
        )
        return ResourceUsageData()