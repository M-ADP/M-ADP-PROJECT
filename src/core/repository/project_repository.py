from abc import ABC, abstractmethod

from src.core.domain.project import Project
from src.core.repository.base import Repository


class ProjectRepository(Repository[Project], ABC):
    """프로젝트 Repository 추상 클래스"""

    @abstractmethod
    async def count_by_user(self, user_id: int) -> int:
        """사용자의 프로젝트 개수를 조회합니다."""
        pass

    @abstractmethod
    async def exists_by_name(
        self,
        user_id: int,
        name: str,
        exclude_project_id: int | None = None,
    ) -> bool:
        """프로젝트 이름 중복 여부를 확인합니다."""
        pass

    @abstractmethod
    async def get_by_id_for_user(self, project_id: int, user_id: int) -> Project | None:
        """사용자의 프로젝트를 ID로 조회합니다."""
        pass

    @abstractmethod
    async def get_by_id(self, project_id: int) -> Project | None:
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
    async def update_name(self, project_id: int, name: str) -> Project:
        """프로젝트 이름을 업데이트합니다."""
        pass

    @abstractmethod
    async def list_by_user(
        self,
        user_id: int,
        limit: int,
        cursor: int | None = None,
    ) -> list[Project]:
        """사용자의 프로젝트 목록을 조회합니다."""
        pass

    @abstractmethod
    async def update_resource(
        self,
        project_id: int,
        max_cpu: float | None = None,
        max_memory: float | None = None,
        max_disk: float | None = None,
    ) -> Project:
        """프로젝트 리소스를 업데이트합니다."""
        pass

    @abstractmethod
    async def get_by_ids(self, project_ids: list[int]) -> list[Project]:
        """프로젝트 ID 목록으로 프로젝트들을 조회합니다."""
        pass
