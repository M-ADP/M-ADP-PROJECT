from abc import ABC, abstractmethod


class DnsClient(ABC):
    @abstractmethod
    async def delete_by_project(
        self,
        project_id: int,
        user_id: int,
        role: str,
    ) -> None:
        """프로젝트의 모든 DNS를 삭제합니다."""
        ...
