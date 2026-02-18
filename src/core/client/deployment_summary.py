from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DeploymentSummaryItem:
    project_id: str
    running: int = 0
    warning: int = 0
    state: str = "STOPPED"
    message: str = ""


class DeploymentSummaryClient(ABC):
    @abstractmethod
    async def get_summary_batch(
        self,
        project_ids: list[str],
    ) -> list[DeploymentSummaryItem]:
        """프로젝트 배포 요약 정보를 배치로 조회합니다."""
        ...
