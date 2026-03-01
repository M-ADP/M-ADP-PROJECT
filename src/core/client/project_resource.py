from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.domain.port import Port
    from src.core.domain.project import Project


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
    async def create(self, user_id: int, role: str, project: "Project") -> None:
        """프로젝트(namespace) 생성"""
        ...

    @abstractmethod
    async def delete(self, user_id: int, role: str, project: "Project") -> None:
        """프로젝트(namespace) 삭제"""
        ...

    @abstractmethod
    async def open_port(self, user_id: int, role: str, project: "Project", port: "Port") -> None:
        """포트 오픈 (gateway 자원 생성)"""
        ...

    @abstractmethod
    async def close_port(self, user_id: int, role: str, project: "Project", port: "Port") -> None:
        """포트 닫기 (gateway 자원 삭제)"""
        ...

    @abstractmethod
    async def update_port(
        self,
        user_id: int,
        role: str,
        project: "Project",
        original_port: "Port",
        updated_port: "Port",
    ) -> None:
        """포트 업데이트 (gateway 자원 수정)"""
        ...

    @abstractmethod
    async def allocate(self, user_id: int, role: str, project: "Project") -> None:
        """가용 자원 할당 (Resource Quota)"""
        ...

    @abstractmethod
    async def get_usage(
        self,
        project: "Project",
        days: int = 7,
        interval_minutes: int = 60,
    ) -> ResourceUsageData:
        """최근 N일의 리소스 사용량 시계열을 조회합니다."""
        ...


class MockProjectResourceClient(ProjectResourceClient):
    """프로젝트 리소스 접근 Mock 클라이언트"""

    async def create(self, user_id: int, role: str, project: "Project") -> None:
        print(f"namespace 생성: {project.name}")
        return None

    async def delete(self, user_id: int, role: str, project: "Project") -> None:
        print(f"namespace 삭제: {project.name}")
        return None

    async def open_port(self, user_id: int, role: str, project: "Project", port: "Port") -> None:
        print(f"gateway 자원 생성: {project.name}:{port.from_port}")
        return None

    async def close_port(self, user_id: int, role: str, project: "Project", port: "Port") -> None:
        print(f"gateway 자원 삭제: {project.name}:{port.from_port}")
        return None

    async def update_port(
        self,
        user_id: int,
        role: str,
        project: "Project",
        original_port: "Port",
        updated_port: "Port",
    ) -> None:
        print(f"gateway 자원 수정: {project.name}:{original_port.from_port} -> {updated_port.from_port}")
        return None

    async def allocate(self, user_id: int, role: str, project: "Project") -> None:
        print(f"Resource Quota 자원 생성: {project.name}")
        return None

    async def get_usage(
        self,
        project: "Project",
        days: int = 7,
        interval_minutes: int = 60,
    ) -> ResourceUsageData:
        print(
            f"프로젝트 {project.id} 최근 {days}일 리소스 사용량 조회 "
            f"(간격 {interval_minutes}분)"
        )
        return ResourceUsageData()