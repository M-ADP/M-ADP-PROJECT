from fastapi import APIRouter, Depends

from src.app.project.schemas import *
from src.app.project.usecase import (
    CreateProjectUseCase,
    UpdateProjectNameUseCase,
    DeleteProjectUseCase,
)
from src.api.deps.auth import UserInfo, get_user_info
from src.core.schemas import SuccessResponse

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=SuccessResponse[ProjectResponse], status_code=201)
async def create_project_endpoint(
    payload: ProjectCreate,
    user: UserInfo = Depends(get_user_info),
    usecase: CreateProjectUseCase = Depends(CreateProjectUseCase),
) -> SuccessResponse[ProjectResponse]:
    project = await usecase(payload, user_id=user.user_id)
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
    usecase: UpdateProjectNameUseCase = Depends(UpdateProjectNameUseCase),
) -> SuccessResponse[ProjectResponse]:
    project = await usecase(project_id, payload, user_id=user.user_id)
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
    usecase: DeleteProjectUseCase = Depends(DeleteProjectUseCase),
) -> SuccessResponse[ProjectResponse]:
    project = await usecase(project_id, user_id=user.user_id)
    return SuccessResponse(
        message="프로젝트가 삭제되었습니다.",
        data=ProjectResponse.model_validate(project),
    )
