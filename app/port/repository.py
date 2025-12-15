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
