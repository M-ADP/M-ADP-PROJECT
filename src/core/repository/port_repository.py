from abc import ABC, abstractmethod

from src.core.domain.port import Port
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

    @abstractmethod
    async def insert(self, port: Port) -> Port:
        """포트를 삽입합니다."""
        pass

    @abstractmethod
    async def delete(self, port: Port) -> None:
        """포트를 삭제합니다."""
        pass

    @abstractmethod
    async def update(
        self,
        project_id: str,
        port_id: str,
        from_ip: str,
        from_port: int,
        port_number: int,
        protocol: str,
    ) -> Port:
        """포트를 업데이트합니다."""
        pass
