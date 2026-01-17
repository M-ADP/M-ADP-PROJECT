from sqlalchemy.ext.asyncio import AsyncSession

from src.app.port import repository as port_repository
from src.app.port.exceptions import PortNotFound
from src.app.port.models import Port
from src.app.project import repository as project_repository
from src.app.project.exceptions import ProjectNotFound


class DeletePortUseCase:
    """포트를 삭제하는 유즈케이스"""

    async def __call__(
        self,
        project_id: str,
        port_id: str,
        user_id: str,
        session: AsyncSession,
    ) -> Port:
        project = await project_repository.get_by_id_for_user(session, project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        port = await port_repository.get_by_id_for_project(
            session=session,
            project_id=project_id,
            port_id=port_id,
        )
        if port is None:
            raise PortNotFound()

        await port_repository.delete(session, port)
        return port
