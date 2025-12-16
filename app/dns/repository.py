from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dns.models import DNS


async def exists_by_dns_name(
    session: AsyncSession,
    dns_name: str,
    exclude_dns_id: str | None = None,
) -> bool:
    conditions = [DNS.dns_name == dns_name]
    if exclude_dns_id:
        conditions.append(DNS.id != exclude_dns_id)

    stmt = select(DNS.id).where(*conditions).limit(1)
    result = await session.execute(stmt)
    return result.first() is not None


async def exists_by_project(session: AsyncSession, project_id: str) -> bool:
    stmt = select(DNS.id).where(DNS.project_id == project_id).limit(1)
    result = await session.execute(stmt)
    return result.first() is not None


async def get_by_project(session: AsyncSession, project_id: str) -> DNS | None:
    stmt = select(DNS).where(DNS.project_id == project_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_id_for_project(
    session: AsyncSession, dns_id: str, project_id: str
) -> DNS | None:
    stmt = select(DNS).where(DNS.id == dns_id, DNS.project_id == project_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def insert(session: AsyncSession, dns: DNS) -> DNS:
    session.add(dns)
    await session.flush()
    return dns


async def delete(session: AsyncSession, dns: DNS) -> None:
    await session.delete(dns)
    await session.flush()
