from sqlalchemy.ext.asyncio import AsyncSession

from src.app.port import repository as port_repository
from src.app.port.schemas import PortResponse
from src.app.project import repository as project_repository
from src.app.project.exceptions import ProjectNotFound
from src.core.schemas import CursorPage


class ListPortsUseCase:
    """포트 목록을 조회하는 유즈케이스"""

    async def __call__(
        self,
        project_id: str,
        user_id: str,
        session: AsyncSession,
        limit: int,
        cursor: str | None = None,
    ) -> CursorPage[PortResponse]:
        project = await project_repository.get_by_id_for_user(session, project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        ports = await port_repository.list_by_project(
            session=session,
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
