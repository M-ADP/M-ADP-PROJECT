from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class UniqueUsersData:
    dau: int
    wau: int
    mau: int


class ProjectMonitoringClient(ABC):
    @abstractmethod
    async def get_unique_users(self, project_id: str) -> UniqueUsersData:
        """프로젝트의 고유 사용자 (DAU/WAU/MAU) 조회"""
        ...
