from abc import ABC, abstractmethod

from src.core.domain.project import ProjectInvitation
from src.core.repository.base import Repository


class ProjectInvitationRepository(Repository[ProjectInvitation], ABC):
    """프로젝트 초대 Repository 추상 클래스"""

    @abstractmethod
    async def get_pending_by_project_and_user(
        self,
        project_id: int,
        invitee_user_id: int,
    ) -> ProjectInvitation | None:
        """프로젝트와 대상 사용자 ID로 대기 중인 초대를 조회합니다."""
        pass

    @abstractmethod
    async def get_pending_by_token_hash(
        self,
        project_id: int,
        token_hash: str,
    ) -> ProjectInvitation | None:
        """프로젝트와 토큰 해시로 대기 중인 초대를 조회합니다."""
        pass

    @abstractmethod
    async def get_by_id(
        self,
        project_id: int,
        invitation_id: int,
    ) -> ProjectInvitation | None:
        """프로젝트와 초대 ID로 초대를 조회합니다."""
        pass

    @abstractmethod
    async def list_by_project(
        self,
        project_id: int,
        status: str | None,
        limit: int,
        cursor: int | None = None,
    ) -> list[ProjectInvitation]:
        """프로젝트의 초대 목록을 조회합니다."""
        pass

    @abstractmethod
    async def insert(self, invitation: ProjectInvitation) -> ProjectInvitation:
        """초대를 추가합니다."""
        pass

    @abstractmethod
    async def update_status(
        self,
        invitation_id: int,
        status: str,
    ) -> ProjectInvitation | None:
        """초대 상태를 변경합니다."""
        pass

    @abstractmethod
    async def rotate_token(
        self,
        invitation_id: int,
        token_hash: str,
        expires_at,
    ) -> ProjectInvitation | None:
        """초대 토큰 해시와 만료 시간을 갱신합니다."""
        pass
