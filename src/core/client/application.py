from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, TypeAlias


ApplicationHealthStatus: TypeAlias = Literal[
    "RUNNING",
    "PENDING",
    "BUILDING",
    "DEPLOYING",
    "STOPPED",
    "FAILED",
]


@dataclass
class ApplicationItemData:
    id: int
    name: str
    runtime: str | None = None
    pod_count: int = 0
    exposed_port: int | None = None
    cpu_usage_percent: float | None = None
    ram_usage_percent: float | None = None
    health_status: ApplicationHealthStatus = "STOPPED"


@dataclass
class DeploymentSummaryItem:
    project_id: int
    running: int = 0
    warning: int = 0
    state: str = "STOPPED"


class ApplicationClient(ABC):
    @abstractmethod
    async def list_by_project(
        self,
        project_id: int,
        user_id: int,
        role: str,
    ) -> list[ApplicationItemData]:
        """프로젝트의 앱 배포 목록을 조회합니다."""
        ...

    @abstractmethod
    async def get_summary_batch(
        self,
        project_ids: list[int],
        user_id: int,
        role: str,
    ) -> list[DeploymentSummaryItem]:
        """프로젝트 배포 요약 정보를 배치로 조회합니다."""
        ...
