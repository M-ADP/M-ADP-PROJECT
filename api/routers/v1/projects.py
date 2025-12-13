from fastapi import APIRouter, Depends

from app.project.schemas import *
from app.project.service import *
from api.deps.auth import UserInfo, get_user_info
from api.deps.db import get_db_session
from core.schemas import SuccessResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=SuccessResponse[ProjectResponse], status_code=201)
async def create_project_endpoint(
    payload: ProjectCreate,
    user: UserInfo = Depends(get_user_info),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[ProjectResponse]:
    async with session.begin():
        project = await create_project(payload, user_id=user.user_id, session=session)
    return SuccessResponse(
        message="프로젝트가 생성되었습니다.",
        data=ProjectResponse.model_validate(project),
    )


@router.patch(
    "/{project_id}/name",
    response_model=SuccessResponse[ProjectResponse],
    status_code=200,
)
async def update_project_name_endpoint(
    project_id: str,
    payload: ProjectNameUpdate,
    user: UserInfo = Depends(get_user_info),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[ProjectResponse]:
    async with session.begin():
        project = await update_project_name(
            project_id,
            payload,
            user_id=user.user_id,
            session=session,
        )
    return SuccessResponse(
        message="프로젝트 이름이 변경되었습니다.",
        data=ProjectResponse.model_validate(project),
    )


@router.delete(
    "/{project_id}",
    response_model=SuccessResponse[ProjectResponse],
    status_code=200,
)
async def delete_project_endpoint(
    project_id: str,
    user: UserInfo = Depends(get_user_info),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[ProjectResponse]:
    async with session.begin():
        project = await delete_project(
            project_id,
            user_id=user.user_id,
            session=session,
        )
    return SuccessResponse(
        message="프로젝트가 삭제되었습니다.",
        data=ProjectResponse.model_validate(project),
    )
