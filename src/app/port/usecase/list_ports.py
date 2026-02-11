from src.app.port.schemas import PortResponse
from src.app.project.exceptions import ProjectNotFound
from src.core.schemas import CursorPage
from src.core.usecase import BaseUseCase


class ListPortsUseCase(BaseUseCase):
    """포트 목록을 조회하는 유즈케이스"""

    async def execute(
        self,
        project_id: str,
        user_id: str,
        limit: int,
        cursor: str | None = None,
    ) -> CursorPage[PortResponse]:
        project = await self.uow.project.get_by_id(project_id)
        if project is None:
            raise ProjectNotFound()

        has_access = await self.uow.project_member.has_access(project_id, user_id)
        if not has_access:
            raise ProjectNotFound()

        ports = await self.uow.port.list_by_project(
            project_id=project_id,
            limit=limit + 1,
            cursor=cursor,
        )
        has_next = len(ports) > limit
        items = ports[:limit]

        return CursorPage(
            items=[PortResponse.model_validate(port) for port in items],
            has_next=has_next,
        )
