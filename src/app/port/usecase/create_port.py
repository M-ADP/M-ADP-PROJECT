from sqlalchemy.ext.asyncio import AsyncSession

from src.app.port import repository as port_repository
from src.app.port.exceptions import PortAlreadyExists
from src.app.port.models import Port
from src.app.port.schemas import PortCreate
from src.app.project import repository as project_repository
from src.app.project.exceptions import ProjectNotFound
from src.common.id_generator import generate_sonyflake_id


class CreatePortUseCase:
    """포트를 생성하는 유즈케이스"""

    async def __call__(
        self,
        project_id: str,
        request: PortCreate,
        user_id: str,
        session: AsyncSession,
    ) -> Port:
        project = await project_repository.get_by_id_for_user(session, project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        if await port_repository.exists_by_from_port(
            session,
            project_id,
            request.from_port,
            exclude_port_id=None,
        ):
            raise PortAlreadyExists()

        port_row = Port(
            id=generate_sonyflake_id(),
            project_id=project_id,
            from_ip=request.from_ip,
            from_port=request.from_port,
            port_number=request.port_number,
            protocol=request.protocol,
        )
        return await port_repository.insert(session, port_row)
