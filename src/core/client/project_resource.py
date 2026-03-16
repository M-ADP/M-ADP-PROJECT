from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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
