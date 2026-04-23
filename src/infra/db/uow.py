from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.uow import UnitOfWork
from src.core.repository import (
    ProjectRepository,
    ProjectMemberRepository,
    ProjectInvitationRepository,
)
from src.infra.db.project.invitation_repository import ProjectInvitationRepositoryImpl
from src.infra.db.project.repository import ProjectRepositoryImpl
from src.infra.db.project.member_repository import ProjectMemberRepositoryImpl


class SQLAlchemyUnitOfWork(UnitOfWork):

    def __init__(self, session: AsyncSession):
        self._session = session
        self._project_repository: ProjectRepository | None = None
        self._project_member_repository: ProjectMemberRepository | None = None
        self._project_invitation_repository: ProjectInvitationRepository | None = None

    async def __aenter__(self) -> Self:
        await self._session.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        """트랜잭션 커밋"""
        await self._session.commit()

    async def rollback(self) -> None:
        """트랜잭션 롤백"""
        await self._session.rollback()

    @property
    def session(self) -> AsyncSession:
        """데이터베이스 세션"""
        return self._session

    @property
    def project(self) -> ProjectRepository:
        """프로젝트 Repository"""
        if self._project_repository is None:
            self._project_repository = ProjectRepositoryImpl(self._session)
        return self._project_repository

    @property
    def project_member(self) -> ProjectMemberRepository:
        """프로젝트 멤버 Repository"""
        if self._project_member_repository is None:
            self._project_member_repository = ProjectMemberRepositoryImpl(self._session)
        return self._project_member_repository

    @property
    def project_invitation(self) -> ProjectInvitationRepository:
        """프로젝트 초대 Repository"""
        if self._project_invitation_repository is None:
            self._project_invitation_repository = ProjectInvitationRepositoryImpl(
                self._session
            )
        return self._project_invitation_repository

