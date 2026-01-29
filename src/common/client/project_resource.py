from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from src.app.dns.schemas import DNSCreate, DNSPortBinding, DNSUpdate
from src.app.port.schemas import PortCreate, PortUpdate
from src.app.project.schemas import ProjectCreate, ProjectResourceUpdate


@dataclass
class MetricPointData:
    timestamp: str
    value: float


@dataclass
class ResourceUsageData:
    cpu: list[MetricPointData] = field(default_factory=list)
    memory: list[MetricPointData] = field(default_factory=list)
    disk: list[MetricPointData] = field(default_factory=list)
    network: list[MetricPointData] = field(default_factory=list)
    traffic_per_hour: list[MetricPointData] = field(default_factory=list)


class ProjectResourceClient(ABC):
    @abstractmethod
    async def create(self, user_id: str, project: ProjectCreate): ...

    @abstractmethod
    async def delete(self, user_id: str, name: str): ...

    @abstractmethod
    async def open_port(self, user_id: str, name: str, port: PortCreate): ...

    @abstractmethod
    async def close_port(self, user_id: str, name: str, port_id: str): ...

    @abstractmethod
    async def update_port(self, user_id: str, name: str, port_id: int, port: PortUpdate): ...

    @abstractmethod
    async def create_dns(self, user_id: str, name: str, dns: DNSCreate): ...

    @abstractmethod
    async def delete_dns(self, user_id: str, name: str, dns_id: str): ...

    @abstractmethod
    async def update_dns(self, user_id: str, name: str, dns_id: str, dns: DNSUpdate): ...

    @abstractmethod
    async def mapping_dns_and_port(self, user_id: str, name: str, dns_id: str, port_binding: DNSPortBinding): ...

    @abstractmethod
    async def allocate(self, user_id: str, name: str, resource: ProjectResourceUpdate):
        """가용 자원 할당"""
        ...

    @abstractmethod
    async def get_usage(
        self,
        project_id: str,
        days: int = 7,
        interval_minutes: int = 60,
    ) -> ResourceUsageData:
        """최근 N일의 리소스 사용량 시계열을 조회합니다."""
        ...

    @abstractmethod
    async def verify_password(
        self,
        user_id: str,
        password: str,
    ) -> bool: ...


class MockProjectResourceClient(ProjectResourceClient):
    """프로젝트 리소스 접근 Mock 클라이언트"""

    async def create(self, user_id: str, project: ProjectCreate) -> None:
        print("namespace 생성")
        return None

    async def delete(self, user_id: str, name: str) -> None:
        print("namespace 삭제")
        return None

    async def open_port(self, user_id: str, name: str, port: PortCreate) -> None:
        print("gateway 자원 생성")
        return None

    async def close_port(self, user_id: str, name: str, port_id: str) -> None:
        print("gateway 자원 삭제")
        return None

    async def update_port(self, user_id: str, name: str, port_id: int, port: PortUpdate) -> None:
        print("gateway 자원 수정")
        return None

    async def create_dns(self, user_id: str, name: str, dns: DNSCreate) -> None:
        print("ExternalDNS 자원 생성")
        return None

    async def delete_dns(self, user_id: str, name: str, dns_id: str) -> None:
        print("ExternalDNS 자원 삭제")
        return None

    async def update_dns(self, user_id: str, name: str, dns_id: str, dns: DNSUpdate) -> None:
        print("ExternalDNS 자원 수정")
        return None

    async def mapping_dns_and_port(self, user_id: str, name: str, dns_id: str, port_binding: DNSPortBinding) -> None:
        print("ExternalDNS 자원과 gateway 자원 매핑")
        return None

    async def allocate(self, user_id: str, name: str, resource: ProjectResourceUpdate) -> None:
        print("Resource Quota 자원 생성")
        return None

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

    async def verify_password(
        self,
        user_id: str,
        password: str,
    ) -> bool:
        print(f"사용자 {user_id} 비밀번호 검증")
        return True
