from fastapi import Depends

from src.app.project.exceptions import ProjectNotFound
from src.app.project.schemas import ProjectMemberResponse
from src.common.schemas import CursorPage
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.user import UserClient
from src.dependencies.uow import get_uow
from src.dependencies.client.user import get_user_client


class ListProjectMembersUseCase(BaseUseCase):
    """프로젝트 멤버 목록을 조회하는 유즈케이스"""

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        user_client: UserClient = Depends(get_user_client),
    ):
        self.uow = uow
        self.user_client = user_client

    async def __call__(
        self,
        project_id: int,
        user_id: int,
        limit: int = 20,
        cursor: int | None = None,
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

            user_infos = {
                info.user_id: info
                for m in members
                if (info := await self.user_client.get_user(m.user_id)) is not None
            }

            return CursorPage(
                items=[
                    ProjectMemberResponse(
                        user_id=m.user_id,
                        username=user_infos[m.user_id].username if m.user_id in user_infos else m.user_id,
                        profile_image=user_infos[m.user_id].profile_image if m.user_id in user_infos else None,
                        role=m.role,
                        joined_at=m.joined_at,
                    )
                    for m in members
                ],
                has_next=has_next,
            )
