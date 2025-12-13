from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.project.models import Project


async def count_by_user(session: AsyncSession, user_id: str) -> int:
    stmt = select(func.count()).select_from(Project).where(Project.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one()


async def exists_by_name(
    session: AsyncSession,
    user_id: str,
    name: str,
    exclude_project_id: str | None = None,
) -> bool:
    conditions = [
        Project.user_id == user_id,
        func.lower(Project.name) == func.lower(name),
    ]
    if exclude_project_id:
        conditions.append(Project.id != exclude_project_id)

    stmt = select(Project.id).where(*conditions).limit(1)
    result = await session.execute(stmt)
    return result.first() is not None


async def get_by_id_for_user(
    session: AsyncSession, project_id: str, user_id: str
) -> Project | None:
    stmt = select(Project).where(Project.id == project_id, Project.user_id == user_id)
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    return row


async def insert(session: AsyncSession, project: Project) -> Project:
    session.add(project)
    await session.flush()
    return project
