from sqlalchemy.ext.asyncio import AsyncSession

from src.app.port import repository as port_repository
from src.app.port.exceptions import PortAlreadyExists, PortNotFound
from src.app.port.models import Port
from src.app.port.schemas import PortUpdate
from src.app.project import repository as project_repository
from src.app.project.exceptions import ProjectNotFound


class UpdatePortUseCase:
    """포트를 업데이트하는 유즈케이스"""

    async def __call__(
        self,
        project_id: str,
        port_id: str,
        request: PortUpdate,
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

        if await port_repository.exists_by_from_port(
            session,
            project_id,
            request.from_port,
            exclude_port_id=port_id,
        ):
            raise PortAlreadyExists()

        port.update(
            from_ip=request.from_ip,
            from_port=request.from_port,
            port_number=request.port_number,
            protocol=request.protocol
        )
        await session.flush()
        return port
