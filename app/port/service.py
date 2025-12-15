from sqlalchemy.ext.asyncio import AsyncSession

from app.port import repository as port_repository
from app.port.exceptions import PortAlreadyExists
from app.port.models import Port
from app.port.schemas import PortCreate
from app.project import repository as project_repository
from app.project.exceptions import ProjectNotFound
from core.id_generator import generate_sonyflake_id


async def create_port(
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
