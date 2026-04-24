from fastapi import APIRouter, Depends, Path

from src.app.project.schemas import ProjectUniqueUsersResponse
from src.app.project.usecase.get_project_unique_users import GetProjectUniqueUsersUseCase
from src.common.schemas import SuccessResponse
from src.dependencies.auth import UserInfo, get_user_info

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get(
    "/project/{project_id}/users",
    response_model=SuccessResponse[ProjectUniqueUsersResponse],
    status_code=200,
)
async def get_project_unique_users_endpoint(
    project_id: int = Path(..., description="조회할 프로젝트 ID"),
    user: UserInfo = Depends(get_user_info),
    usecase: GetProjectUniqueUsersUseCase = Depends(GetProjectUniqueUsersUseCase),
) -> SuccessResponse[ProjectUniqueUsersResponse]:
    result = await usecase(project_id=project_id, user_id=user.user_id)
    return SuccessResponse(
        message="프로젝트 고유 사용자를 조회했습니다.",
        data=result,
    )
