from fastapi import APIRouter, Depends

from app.project.schemas import ProjectCreate, ProjectResponse
from app.project.service import create_project
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
    project = await create_project(payload, user_id=user.user_id, session=session)
    return SuccessResponse(
        message="프로젝트가 생성되었습니다.",
        data=ProjectResponse.model_validate(project),
    )
