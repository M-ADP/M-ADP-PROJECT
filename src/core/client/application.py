from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ApplicationItemData:
    id: int
    name: str
    runtime: str | None = None
    pod_count: int = 0
    exposed_port: int | None = None
    cpu_usage_percent: float | None = None
    ram_usage_percent: float | None = None
    health_status: str = "Stopped"


class ApplicationClient(ABC):
    @abstractmethod
    async def list_by_project(
        self,
        project_id: int,
    ) -> list[ApplicationItemData]:
        """프로젝트의 앱 배포 목록을 조회합니다."""
        ...
