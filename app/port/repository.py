from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.port.models import Port


async def exists_by_from_port(
    session: AsyncSession,
    project_id: str,
    from_port: int,
) -> bool:
    stmt = (
        select(Port.id)
        .where(Port.project_id == project_id, Port.from_port == from_port)
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.first() is not None


async def insert(session: AsyncSession, port: Port) -> Port:
    session.add(port)
    await session.flush()
    return port


async def list_by_project(
    session: AsyncSession,
    project_id: str,
    limit: int,
    cursor: str | None = None,
) -> list[Port]:
    conditions = [Port.project_id == project_id]
    if cursor:
        conditions.append(Port.id > cursor)

    stmt = (
        select(Port)
        .where(*conditions)
        .order_by(Port.id)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_by_id_for_project(
    session: AsyncSession,
    project_id: str,
    port_id: str,
) -> Port | None:
    stmt = select(Port).where(Port.id == port_id, Port.project_id == project_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def delete(session: AsyncSession, port: Port) -> None:
    await session.delete(port)
    await session.flush()
