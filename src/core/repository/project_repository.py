from abc import ABC, abstractmethod

from src.app.project.model import Project
from src.core.repository.base import Repository


class ProjectRepository(Repository[Project], ABC):
    """프로젝트 Repository 추상 클래스"""

    @abstractmethod
    async def count_by_user(self, user_id: str) -> int:
        """사용자의 프로젝트 개수를 조회합니다."""
        pass

    @abstractmethod
    async def exists_by_name(
        self,
        user_id: str,
        name: str,
        exclude_project_id: str | None = None,
    ) -> bool:
        """프로젝트 이름 중복 여부를 확인합니다."""
        pass

    @abstractmethod
    async def get_by_id_for_user(self, project_id: str, user_id: str) -> Project | None:
        """사용자의 프로젝트를 ID로 조회합니다."""
        pass

    @abstractmethod
    async def get_by_id(self, project_id: str) -> Project | None:
        """프로젝트를 ID로 조회합니다."""
        pass

    @abstractmethod
    async def insert(self, project: Project) -> Project:
        """프로젝트를 삽입합니다."""
        pass

    @abstractmethod
    async def delete(self, project: Project) -> None:
        """프로젝트를 삭제합니다."""
        pass

    @abstractmethod
    async def update_name(self, project_id: str, name: str) -> Project:
        """프로젝트 이름을 업데이트합니다."""
        pass

    @abstractmethod
    async def list_by_user(
        self,
        user_id: str,
        limit: int,
        cursor: str | None = None,
    ) -> list[Project]:
        """사용자의 프로젝트 목록을 조회합니다."""
        pass

    @abstractmethod
    async def update_resource(
        self,
        project_id: str,
        max_cpu: float | None = None,
        max_memory: float | None = None,
        max_disk: float | None = None,
    ) -> Project:
        """프로젝트 리소스를 업데이트합니다."""
        pass

    @abstractmethod
    async def get_by_ids(self, project_ids: list[str]) -> list[Project]:
        """프로젝트 ID 목록으로 프로젝트들을 조회합니다."""
        pass
