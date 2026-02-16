from fastapi import Depends

from src.app.project.exceptions import ProjectNotFound
from src.core.domain.project import ProjectMember
from src.app.project.schemas import ProjectMemberResponse
from src.common.schemas import CursorPage
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.dependencies.uow import get_uow


class ListProjectMembersUseCase(BaseUseCase):
    """프로젝트 멤버 목록을 조회하는 유즈케이스"""

    def __init__(self, uow: UnitOfWork = Depends(get_uow)):
        self.uow = uow

    async def __call__(
        self,
        project_id: str,
        user_id: str,
        limit: int = 20,
        cursor: str | None = None,
    ) -> CursorPage[ProjectMemberResponse]:
        async with self.uow:
            # 프로젝트 존재 여부 확인 (소유자 또는 멤버만 조회 가능)
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            # 프로젝트 접근 권한 확인
            has_access = await self.uow.project_member.has_access(project_id, user_id)
            if not has_access:
                raise ProjectNotFound()

            # 멤버 목록 조회
            members = await self.uow.project_member.list_by_project(
                project_id=project_id,
                limit=limit + 1,
                cursor=cursor,
            )

            has_next = len(members) > limit
            if has_next:
                members = members[:limit]

            return CursorPage(
                items=[ProjectMemberResponse.model_validate(m) for m in members],
                has_next=has_next,
            )
