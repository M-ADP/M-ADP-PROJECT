from enum import Enum

from src.app.dns.schemas import DNSCreate, DNSPortBinding, DNSUpdate
from src.app.port.schemas import PortCreate, PortUpdate
from src.app.project.schemas import ProjectCreate, ProjectResourceUpdate
from src.common.client.http import HttpClient
from src.common.client.project_resource import ProjectResourceClient, ResourceUsageData
from src.common.config.resource_server import ResourceServerConfig
from src.infra.client.asyncio_http import AioHttpClient


class ProjectResourceAPIUrls(str, Enum):
    CREATE_PROJECT = "/v1/projects"
    DELETE_PROJECT = "/v1/projects/{name}"
    OPEN_PROJECT_PORT = "/v1/projects/{name}/ports"
    UPDATE_PROJECT_PORT = "/v1/projects/{name}/ports/{port_id}"
    CLOSE_PROJECT_PORT = "/v1/projects/{name}/ports/{port_id}"
    CREATE_PROJECT_DNS = "/v1/projects/{name}/dns"
    DELETE_PROJECT_DNS = "/v1/projects/{name}/dns-records/{dns_id}"
    UPDATE_PROJECT_DNS = "/v1/projects/{name}/dns-records/{dns_id}"
    BIND_PROJECT_DNS_PORT = "/v1/projects/{name}/dns-records/{dns_id}/port"
    UPDATE_PROJECT_RESOURCES = "/v1/projects/{name}/resource"


class ProjectResourceClientImpl(ProjectResourceClient):

    def __init__(
            self,
            resource_server_base_url: str = ResourceServerConfig.RESOURCE_SERVER_BASE_URL,
            http_client: HttpClient = AioHttpClient(),
    ):
        self.base_url = resource_server_base_url
        self.http_client = http_client

    async def create(self, user_id: str, project: ProjectCreate) -> None:
        await self.http_client.post(
            self.base_url + ProjectResourceAPIUrls.CREATE_PROJECT,
            headers={"user-id": user_id},
            json=project.model_dump(),
        )

    async def delete(self, user_id: str, name: str) -> None:
        await self.http_client.delete(
            self.base_url + ProjectResourceAPIUrls.DELETE_PROJECT.format(
                name=name
            ),
            headers={"user-id": user_id},
        )

    async def open_port(self, user_id: str, name: str, port: PortCreate) -> None:
        await self.http_client.post(
            self.base_url + ProjectResourceAPIUrls.OPEN_PROJECT_PORT.format(
                name=name
            ),
            headers={"user-id": user_id},
            json=port.model_dump(),
        )

    async def close_port(self, user_id: str, name: str, port_id: str) -> None:
        await self.http_client.delete(
            self.base_url + ProjectResourceAPIUrls.CLOSE_PROJECT_PORT.format(
                name=name, port_id=port_id
            ),
            headers={"user-id": user_id},
        )

    async def update_port(self, user_id: str, name: str, port_id: int, port: PortUpdate) -> None:
        await self.http_client.put(
            self.base_url + ProjectResourceAPIUrls.UPDATE_PROJECT_PORT.format(
                name=name, port_id=port_id
            ),
            headers={"user-id": user_id},
            json=port.model_dump(),
        )

    async def create_dns(self, user_id: str, name: str, dns: DNSCreate) -> None:
        await self.http_client.post(
            self.base_url + ProjectResourceAPIUrls.CREATE_PROJECT_DNS.format(name=name),
            headers={"user-id": user_id},
            json=dns.model_dump(),
        )

    async def delete_dns(self, user_id: str, name: str, dns_id: str) -> None:
        await self.http_client.delete(
            self.base_url + ProjectResourceAPIUrls.DELETE_PROJECT_DNS.format(name=name, dns_id=dns_id),
            headers={"user-id": user_id},
        )

    async def update_dns(self, user_id: str, name: str, dns_id: str, dns: DNSUpdate) -> None:
        await self.http_client.patch(
            self.base_url + ProjectResourceAPIUrls.UPDATE_PROJECT_DNS.format(name=name, dns_id=dns_id),
            headers={"user-id": user_id},
            json=dns.model_dump(),
        )

    async def mapping_dns_and_port(self, user_id: str, name: str, dns_id: str, port_binding: DNSPortBinding) -> None:
        await self.http_client.patch(
            self.base_url + ProjectResourceAPIUrls.BIND_PROJECT_DNS_PORT.format(name=name, dns_id=dns_id),
            headers={"user-id": user_id},
            json=port_binding.model_dump(),
        )

    async def allocate(self, user_id: str, name: str, resource: ProjectResourceUpdate) -> None:
        await self.http_client.patch(
            self.base_url + ProjectResourceAPIUrls.UPDATE_PROJECT_RESOURCES.format(name=name),
            headers={"user-id": user_id},
            json=resource.model_dump(),
        )

    async def get_usage( # 이거 어디 쓰는거임?
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
