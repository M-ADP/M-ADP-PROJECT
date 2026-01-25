from src.app.project.exceptions import ProjectNotFound
from src.app.project.model import ProjectMember
from src.app.project.schemas import ProjectMemberResponse
from src.core.schemas import CursorPage
from src.core.usecase import BaseUseCase


class ListProjectMembersUseCase(BaseUseCase):
    """프로젝트 멤버 목록을 조회하는 유즈케이스"""

    async def execute(
        self,
        project_id: str,
        user_id: str,
        limit: int = 20,
        cursor: str | None = None,
    ) -> CursorPage[ProjectMemberResponse]:
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
