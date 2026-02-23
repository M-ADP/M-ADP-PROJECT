from fastapi import APIRouter, Depends, Query, Response, status

from src.app.project.schemas import *
from src.app.project.usecase import (
    CreateProjectUseCase,
    UpdateProjectNameUseCase,
    DeleteProjectUseCase,
    ListProjectsUseCase,
    GetProjectUseCase,
    UpdateProjectResourceUseCase,
    ListProjectMembersUseCase,
    AddProjectMemberUseCase,
    RemoveProjectMemberUseCase,
    TransferProjectOwnershipUseCase,
    CheckProjectAvailableUseCase,
)
from src.dependencies.auth import UserInfo, get_user_info
from src.common.schemas import CursorPage, SuccessResponse

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


@router.get(
    "",
    response_model=SuccessResponse[CursorPage[ProjectListItemResponse]],
    status_code=200,
)
async def list_projects_endpoint(
    cursor: str | None = Query(
        None,
        description="다음 페이지 커서(id). 지정하면 해당 커서 이후부터 조회",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="한 번에 가져올 프로젝트 수 (1~100, 기본 20)",),
    user: UserInfo = Depends(get_user_info),
    usecase: ListProjectsUseCase = Depends(ListProjectsUseCase),
) -> SuccessResponse[CursorPage[ProjectListItemResponse]]:
    projects = await usecase(user_id=user.user_id, limit=limit, cursor=cursor)
    return SuccessResponse(
        message="프로젝트 목록을 조회했습니다.",
        data=projects,
    )


@router.get(
    "/available",
    status_code=status.HTTP_200_OK,
    response_class=Response,
)
async def check_project_available_endpoint(
    project_id: str = Query(..., description="확인할 프로젝트 ID"),
    user: UserInfo = Depends(get_user_info),
    usecase: CheckProjectAvailableUseCase = Depends(CheckProjectAvailableUseCase),
) -> Response:
    is_member = await usecase(project_id=project_id, user_id=user.user_id)
    if is_member:
        return Response(status_code=status.HTTP_200_OK)
    return Response(status_code=status.HTTP_403_FORBIDDEN)


@router.get(
    "/{project_id}",
    response_model=SuccessResponse[ProjectDetailResponse],
    status_code=200,
)
async def get_project_endpoint(
    project_id: str,
    user: UserInfo = Depends(get_user_info),
    usecase: GetProjectUseCase = Depends(GetProjectUseCase),
) -> SuccessResponse[ProjectDetailResponse]:
    project = await usecase(project_id, user_id=user.user_id)
    return SuccessResponse(
        message="프로젝트를 조회했습니다.",
        data=project,
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


@router.patch(
    "/{project_id}/resource",
    response_model=SuccessResponse[ProjectResponse],
    status_code=200,
)
async def update_project_resource_endpoint(
    project_id: str,
    payload: ProjectResourceUpdate,
    user: UserInfo = Depends(get_user_info),
    usecase: UpdateProjectResourceUseCase = Depends(UpdateProjectResourceUseCase),
) -> SuccessResponse[ProjectResponse]:
    project = await usecase(project_id, request=payload, user_id=user.user_id)
    return SuccessResponse(
        message="프로젝트 리소스가 변경되었습니다.",
        data=ProjectResponse.model_validate(project),
    )


# ===== Project Members =====


@router.get(
    "/{project_id}/members",
    response_model=SuccessResponse[CursorPage[ProjectMemberResponse]],
    status_code=200,
)
async def list_project_members_endpoint(
    project_id: str,
    cursor: str | None = Query(
        None,
        description="다음 페이지 커서(id). 지정하면 해당 커서 이후부터 조회",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="한 번에 가져올 멤버 수 (1~100, 기본 20)",
    ),
    user: UserInfo = Depends(get_user_info),
    usecase: ListProjectMembersUseCase = Depends(ListProjectMembersUseCase),
) -> SuccessResponse[CursorPage[ProjectMemberResponse]]:
    members = await usecase(
        project_id=project_id,
        user_id=user.user_id,
        limit=limit,
        cursor=cursor,
    )
    return SuccessResponse(
        message="멤버 목록을 조회했습니다.",
        data=members,
    )


@router.post(
    "/{project_id}/members",
    response_model=SuccessResponse[ProjectMemberResponse],
    status_code=201,
)
async def add_project_member_endpoint(
    project_id: str,
    payload: ProjectMemberAdd,
    user: UserInfo = Depends(get_user_info),
    usecase: AddProjectMemberUseCase = Depends(AddProjectMemberUseCase),
) -> SuccessResponse[ProjectMemberResponse]:
    member = await usecase(
        project_id=project_id,
        request=payload,
        user_id=user.user_id,
    )
    return SuccessResponse(
        message="멤버가 추가되었습니다.",
        data=member,
    )


@router.delete(
    "/{project_id}/members/{target_user_id}",
    response_model=SuccessResponse[ProjectMemberResponse],
    status_code=200,
)
async def remove_project_member_endpoint(
    project_id: str,
    target_user_id: str,
    user: UserInfo = Depends(get_user_info),
    usecase: RemoveProjectMemberUseCase = Depends(RemoveProjectMemberUseCase),
) -> SuccessResponse[ProjectMemberResponse]:
    member = await usecase(
        project_id=project_id,
        target_user_id=target_user_id,
        user_id=user.user_id,
    )
    return SuccessResponse(
        message="멤버가 제거되었습니다.",
        data=member,
    )


@router.patch(
    "/{project_id}/owner",
    response_model=SuccessResponse[ProjectMemberResponse],
    status_code=200,
)
async def transfer_project_ownership_endpoint(
    project_id: str,
    payload: ProjectOwnerTransfer,
    user: UserInfo = Depends(get_user_info),
    usecase: TransferProjectOwnershipUseCase = Depends(TransferProjectOwnershipUseCase),
) -> SuccessResponse[ProjectMemberResponse]:
    new_owner = await usecase(
        project_id=project_id,
        target_user_id=payload.target_user_id,
        user_id=user.user_id,
    )
    return SuccessResponse(
        message="프로젝트 소유자가 변경되었습니다.",
        data=new_owner,
    )
