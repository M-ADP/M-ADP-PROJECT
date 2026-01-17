from sqlalchemy.ext.asyncio import AsyncSession

from src.app.port import repository as port_repository
from src.app.port.exceptions import PortAlreadyExists, PortNotFound
from src.app.port.models import Port
from src.app.port.schemas import PortCreate, PortResponse, PortUpdate
from src.app.project import repository as project_repository
from src.app.project.exceptions import ProjectNotFound
from src.core.schemas import CursorPage
from src.common.id_generator import generate_sonyflake_id


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


async def list_ports(
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


async def update_port(
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
        from_ip = request.from_ip,
        from_port = request.from_port,
        port_number = request.port_number,
        protocol = request.protocol
    )
    await session.flush()
    return port


async def delete_port(
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
