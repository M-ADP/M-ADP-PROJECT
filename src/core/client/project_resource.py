from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.domain.project import Project


@dataclass
class ResourceMetricSnapshotData:
    limit: str
    used: str
    percentage: float
    unit: str


@dataclass
class ResourceSnapshotData:
    limit: int
    used: int
    percentage: float


@dataclass
class ProjectResourceSnapshotData:
    project_id: str
    cpu: ResourceMetricSnapshotData
    memory: ResourceMetricSnapshotData
    disk: ResourceMetricSnapshotData
    instance: ResourceSnapshotData


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
        user_id: int,
        days: int = 7,
        interval_minutes: int = 60,
    ) -> ProjectResourceSnapshotData:
        """프로젝트의 현재 리소스 사용량 스냅샷을 조회합니다."""
        ...
