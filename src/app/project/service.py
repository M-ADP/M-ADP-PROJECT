from sqlalchemy.ext.asyncio import AsyncSession

from src.app.project.schemas import ProjectCreate, ProjectNameUpdate
from src.app.project.exceptions import (
    ProjectLimitExceeded,
    ProjectNameAlreadyExists,
    ProjectNotFound,
)
from src.app.project.models import Project
from src.app.project import repository
from src.core.id_generator import generate_sonyflake_id

PROJECT_LIMIT = 3


async def create_project(
    request: ProjectCreate,
    user_id: str,
    session: AsyncSession,
) -> Project:
    project_count = await repository.count_by_user(session, user_id)
    if project_count >= PROJECT_LIMIT:
        raise ProjectLimitExceeded()

    if await repository.exists_by_name(session, user_id, request.name):
        raise ProjectNameAlreadyExists()

    project_id = generate_sonyflake_id()
    project_row = Project(
        id=project_id,
        user_id=user_id,
        name=request.name,
        max_cpu=request.max_cpu,
        max_memory=request.max_memory,
        max_disk=request.max_disk,
    )
    return await repository.insert(session, project_row)


async def update_project_name(
    project_id: str,
    request: ProjectNameUpdate,
    user_id: str,
    session: AsyncSession,
) -> Project:
    project = await repository.get_by_id_for_user(session, project_id, user_id)
    if project is None:
        raise ProjectNotFound()

    if await repository.exists_by_name(
        session,
        user_id,
        request.name,
        exclude_project_id=project_id,
    ):
        raise ProjectNameAlreadyExists()

    project.update_name(request.name)
    await session.flush()
    return project


async def delete_project(
    project_id: str,
    user_id: str,
    session: AsyncSession,
) -> Project:
    project = await repository.get_by_id_for_user(session, project_id, user_id)
    if project is None:
        raise ProjectNotFound()

    await repository.delete(session, project)
    return project
