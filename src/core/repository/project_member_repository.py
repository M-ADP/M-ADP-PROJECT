from abc import ABC, abstractmethod

from src.app.project.model import ProjectMember
from src.core.repository.base import Repository


class ProjectMemberRepository(Repository[ProjectMember], ABC):
    """프로젝트 멤버 Repository 추상 클래스"""

    @abstractmethod
    async def list_by_project(
        self,
        project_id: str,
        limit: int,
        cursor: str | None = None,
    ) -> list[ProjectMember]:
        """프로젝트의 멤버 목록을 조회합니다."""
        pass

    @abstractmethod
    async def get_by_project_and_user(
        self,
        project_id: str,
        user_id: str,
    ) -> ProjectMember | None:
        """프로젝트와 사용자 ID로 멤버를 조회합니다."""
        pass

    @abstractmethod
    async def exists_by_project_and_user(
        self,
        project_id: str,
        user_id: str,
    ) -> bool:
        """프로젝트에 해당 사용자가 멤버로 존재하는지 확인합니다."""
        pass

    @abstractmethod
    async def insert(self, member: ProjectMember) -> ProjectMember:
        """멤버를 추가합니다."""
        pass

    @abstractmethod
    async def delete(self, member: ProjectMember) -> None:
        """멤버를 삭제합니다."""
        pass

    @abstractmethod
    async def is_owner(self, project_id: str, user_id: str) -> bool:
        """사용자가 프로젝트 소유자인지 확인합니다."""
        pass

    @abstractmethod
    async def has_access(self, project_id: str, user_id: str) -> bool:
        """사용자가 프로젝트에 접근 권한이 있는지 확인합니다 (소유자 또는 멤버)."""
        pass

    @abstractmethod
    async def list_project_ids_by_user(
        self,
        user_id: str,
        limit: int,
        cursor: str | None = None,
    ) -> list[str]:
        """사용자가 참여한 프로젝트 ID 목록을 조회합니다."""
        pass

    @abstractmethod
    async def get_role(self, project_id: str, user_id: str) -> str | None:
        """프로젝트에서 사용자의 역할을 조회합니다."""
        pass

    @abstractmethod
    async def get_roles_batch(
        self,
        project_ids: list[str],
        user_id: str,
    ) -> dict[str, str]:
        """여러 프로젝트에서 사용자의 역할을 일괄 조회합니다."""
        pass
