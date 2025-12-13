from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.project.models import Project


async def count_by_user(session: AsyncSession, user_id: str) -> int:
    stmt = select(func.count()).select_from(Project).where(Project.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one()


async def exists_by_name(session: AsyncSession, user_id: str, name: str) -> bool:
    stmt = (
        select(Project.id)
        .where(
            Project.user_id == user_id,
            func.lower(Project.name) == func.lower(name),
        )
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.first() is not None


async def insert(session: AsyncSession, project: Project) -> Project:
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project
