from enum import Enum

from fastapi import Depends

from src.app.port.schemas import PortCreate, PortUpdate
from src.app.project.schemas import ProjectCreate, ProjectResourceUpdate
from src.common.client.http import HttpClient
from src.common.client.project_resource import ProjectResourceClient, ResourceUsageData
from src.common.config.resource_server import ResourceServerConfig, get_resource_config
from src.infra.client.asyncio_http import AioHttpClient
from src.infra.client.schemas import (
    ExternalPortCreate,
    ExternalPortUpdate,
    ExternalProjectCreate,
    ExternalResourceUpdate,
)


class ProjectResourceAPIUrls(str, Enum):
    CREATE_PROJECT = "/v1/projects"
    DELETE_PROJECT = "/v1/projects/{name}"
    OPEN_PROJECT_PORT = "/v1/projects/{name}/ports"
    UPDATE_PROJECT_PORT = "/v1/projects/{name}/ports/{port_id}"
    CLOSE_PROJECT_PORT = "/v1/projects/{name}/ports/{port_id}"
    UPDATE_PROJECT_RESOURCES = "/v1/projects/{name}/resource"


class ProjectResourceClientImpl(ProjectResourceClient):

    def __init__(
            self,
            resource_server_config : ResourceServerConfig = Depends(get_resource_config),
            http_client: HttpClient = AioHttpClient(),
    ):
        self.base_url = resource_server_config.RESOURCE_SERVER_BASE_URL
        self.http_client = http_client

    def _convert_cpu(self, val: float | None) -> str | None:
        if val is None:
            return None
        return f"{int(val * 1000)}m"

    def _convert_memory(self, val: float | None) -> str | None:
        if val is None:
            return None
        return f"{int(val)}Mi"

    async def create(self, user_id: str, project_id: str, project: ProjectCreate) -> None:
        payload = ExternalProjectCreate(
            id=project_id,
            name=project.name,
            cpu=self._convert_cpu(project.max_cpu),
            memory=self._convert_memory(project.max_memory),
            disk=self._convert_memory(project.max_disk),
        )
        await self.http_client.post(
            self.base_url + ProjectResourceAPIUrls.CREATE_PROJECT,
            headers={"user-id": user_id},
            json=payload.model_dump(exclude_none=True),
        )

    async def delete(self, user_id: str, name: str) -> None:
        await self.http_client.delete(
            self.base_url + ProjectResourceAPIUrls.DELETE_PROJECT.format(
                name=name
            ),
            headers={"user-id": user_id},
        )

    async def open_port(self, user_id: str, name: str, port: PortCreate) -> None:
        service_id = f"svc-{name}-{port.from_port}"
        payload = ExternalPortCreate(
            service_id=service_id,
            service_name=service_id,
            target_deployment_name=name,
            port=port.from_port,
            target_port=port.from_port,
            protocol=port.protocol.upper(),  # type: ignore
            service_type="ClusterIP",
        )
        await self.http_client.post(
            self.base_url + ProjectResourceAPIUrls.OPEN_PROJECT_PORT.format(
                name=name
            ),
            headers={"user-id": user_id},
            json=payload.model_dump(),
        )

    async def close_port(self, user_id: str, name: str, port_id: str) -> None:
        # port_id is port number string from usecase
        service_id = f"svc-{name}-{port_id}"
        await self.http_client.delete(
            self.base_url + ProjectResourceAPIUrls.CLOSE_PROJECT_PORT.format(
                name=name, port_id=service_id
            ),
            headers={"user-id": user_id},
        )

    async def update_port(self, user_id: str, name: str, port_id: int, port: PortUpdate) -> None:
        # port_id is original port number from usecase
        service_id = f"svc-{name}-{port_id}"
        payload = ExternalPortUpdate(
            service_id=service_id,
            service_name=service_id,
            target_deployment_name=name,
            target_port=port.from_port,
            protocol=port.protocol.upper(), # type: ignore
            service_type="ClusterIP",
        )
        await self.http_client.put(
            self.base_url + ProjectResourceAPIUrls.UPDATE_PROJECT_PORT.format(
                name=name, port_id=port_id
            ),
            headers={"user-id": user_id},
            json=payload.model_dump(exclude_none=True),
        )

    async def allocate(self, user_id: str, name: str, resource: ProjectResourceUpdate) -> None:
        payload = ExternalResourceUpdate(
            cpu=self._convert_cpu(resource.max_cpu),
            memory=self._convert_memory(resource.max_memory),
            disk=self._convert_memory(resource.max_disk),
        )
        await self.http_client.patch(
            self.base_url + ProjectResourceAPIUrls.UPDATE_PROJECT_RESOURCES.format(name=name),
            headers={"user-id": user_id},
            json=payload.model_dump(exclude_none=True),
        )

    async def get_usage(
        self,
        project_id: str,
        days: int = 7,
        interval_minutes: int = 60,
    ) -> ResourceUsageData:
        print(
            f"프로젝트 {project_id} 최근 {days}일 리소스 사용량 조회 "
            f"(간격 {interval_minutes}분)"
        )
        return ResourceUsageData()