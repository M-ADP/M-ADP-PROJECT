from abc import ABC, abstractmethod

from src.app.port.models import Port
from src.core.repository.base import Repository


class PortRepository(Repository[Port], ABC):
    """포트 Repository 추상 클래스"""

    @abstractmethod
    async def exists_by_from_port(
        self,
        project_id: str,
        from_port: int,
        exclude_port_id: str | None = None,
    ) -> bool:
        """포트 중복 여부를 확인합니다."""
        pass

    @abstractmethod
    async def list_by_project(
        self,
        project_id: str,
        limit: int,
        cursor: str | None = None,
    ) -> list[Port]:
        """프로젝트의 포트 목록을 조회합니다."""
        pass

    @abstractmethod
    async def get_by_id_for_project(
        self,
        project_id: str,
        port_id: str,
    ) -> Port | None:
        """프로젝트의 포트를 ID로 조회합니다."""
        pass
