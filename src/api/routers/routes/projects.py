from fastapi import APIRouter, Depends, Path, Query

from src.app.project.schemas import (
    ProjectAvailableResponse,
    ProjectCreate,
    ProjectDetailResponse,
    ProjectListItemResponse,
    ProjectMemberInvitationResponse,
    ProjectMemberInvite,
    ProjectMemberResponse,
    ProjectNameUpdate,
    ProjectOwnerResponse,
    ProjectOwnerTransfer,
    ProjectResourceLimitResponse,
    ProjectResourceUpdate,
    ProjectResponse,
)
from src.app.project.usecase import (
    CreateProjectUseCase,
    UpdateProjectNameUseCase,
    DeleteProjectUseCase,
    ListProjectsUseCase,
    GetProjectUseCase,
    UpdateProjectResourceUseCase,
    ListProjectMembersUseCase,
    AcceptProjectMemberInvitationUseCase,
    CancelProjectMemberInvitationUseCase,
    InviteProjectMemberUseCase,
    ListProjectMemberInvitationsUseCase,
    RemoveProjectMemberUseCase,
    ResendProjectMemberInvitationUseCase,
    TransferProjectOwnershipUseCase,
    CheckProjectAvailableUseCase,
    CheckProjectOwnerUseCase,
    GetProjectResourceLimitUseCase,
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
    project = await usecase(payload, user_id=user.user_id, role=user.role)
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
    cursor: int | None = Query(
        None,
        description="다음 페이지 커서(project id). 지정하면 해당 커서 이후부터 조회",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="한 번에 가져올 프로젝트 수 (1~100, 기본 20)",),
    user: UserInfo = Depends(get_user_info),
    usecase: ListProjectsUseCase = Depends(ListProjectsUseCase),
) -> SuccessResponse[CursorPage[ProjectListItemResponse]]:
    projects = await usecase(user_id=user.user_id, role=user.role, limit=limit, cursor=cursor)
    return SuccessResponse(
        message="프로젝트 목록을 조회했습니다.",
        data=projects,
    )


@router.get(
    "/available",
    status_code=200,
    response_model=SuccessResponse[ProjectAvailableResponse],
)
async def check_project_available_endpoint(
    project_id: int = Query(..., description="확인할 프로젝트 ID"),
    user: UserInfo = Depends(get_user_info),
    usecase: CheckProjectAvailableUseCase = Depends(CheckProjectAvailableUseCase),
) -> SuccessResponse[ProjectAvailableResponse]:
    is_member = await usecase(project_id=project_id, user_id=user.user_id)
    return SuccessResponse(
        message="프로젝트 접근 가능 여부를 조회했습니다.",
        data=ProjectAvailableResponse(status=is_member),
    )


@router.get(
    "/owner",
    status_code=200,
    response_model=SuccessResponse[ProjectOwnerResponse],
)
async def check_project_owner_endpoint(
    project_id: int = Query(..., description="확인할 프로젝트 ID"),
    user: UserInfo = Depends(get_user_info),
    usecase: CheckProjectOwnerUseCase = Depends(CheckProjectOwnerUseCase),
) -> SuccessResponse[ProjectOwnerResponse]:
    is_owner = await usecase(project_id=project_id, user_id=user.user_id)
    return SuccessResponse(
        message="프로젝트 소유자 여부를 조회했습니다.",
        data=ProjectOwnerResponse(status=is_owner),
    )


@router.get(
    "/resource-limit/{project_id}",
    status_code=200,
    response_model=SuccessResponse[ProjectResourceLimitResponse],
)
async def get_project_resource_limit_endpoint(
    project_id: int = Path(..., description="확인할 프로젝트 ID"),
    user: UserInfo = Depends(get_user_info),
    usecase: GetProjectResourceLimitUseCase = Depends(GetProjectResourceLimitUseCase),
) -> SuccessResponse[ProjectResourceLimitResponse]:
    resource_limit = await usecase(project_id=project_id, user_id=user.user_id)
    return SuccessResponse(
        message="프로젝트 최대 리소스 한도를 조회했습니다.",
        data=resource_limit,
    )


@router.get(
    "/{project_id}",
    response_model=SuccessResponse[ProjectDetailResponse],
    status_code=200,
)
async def get_project_endpoint(
    project_id: int,
    user: UserInfo = Depends(get_user_info),
    usecase: GetProjectUseCase = Depends(GetProjectUseCase),
) -> SuccessResponse[ProjectDetailResponse]:
    project = await usecase(project_id, user_id=user.user_id, role=user.role)
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
    project_id: int,
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
    project_id: int,
    user: UserInfo = Depends(get_user_info),
    usecase: DeleteProjectUseCase = Depends(DeleteProjectUseCase),
) -> SuccessResponse[ProjectResponse]:
    project = await usecase(project_id, user_id=user.user_id, role=user.role)
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
    project_id: int,
    payload: ProjectResourceUpdate,
    user: UserInfo = Depends(get_user_info),
    usecase: UpdateProjectResourceUseCase = Depends(UpdateProjectResourceUseCase),
) -> SuccessResponse[ProjectResponse]:
    project = await usecase(project_id, request=payload, user_id=user.user_id, role=user.role)
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
    project_id: int,
    cursor: int | None = Query(
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
    response_model=SuccessResponse[ProjectMemberInvitationResponse],
    status_code=201,
)
async def invite_project_member_endpoint(
    project_id: int,
    payload: ProjectMemberInvite,
    user: UserInfo = Depends(get_user_info),
    usecase: InviteProjectMemberUseCase = Depends(InviteProjectMemberUseCase),
) -> SuccessResponse[ProjectMemberInvitationResponse]:
    invitation = await usecase(
        project_id=project_id,
        request=payload,
        user_id=user.user_id,
    )
    return SuccessResponse(
        message="멤버 초대 메일을 발송했습니다.",
        data=invitation,
    )


add_project_member_endpoint = invite_project_member_endpoint


@router.get(
    "/{project_id}/member-invitations",
    response_model=SuccessResponse[CursorPage[ProjectMemberInvitationResponse]],
    status_code=200,
)
async def list_project_member_invitations_endpoint(
    project_id: int,
    status: str | None = Query(
        "PENDING",
        description="조회할 초대 상태. 기본값은 PENDING",
    ),
    cursor: int | None = Query(
        None,
        description="다음 페이지 커서(id). 지정하면 해당 커서 이후부터 조회",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="한 번에 가져올 초대 수 (1~100, 기본 20)",
    ),
    user: UserInfo = Depends(get_user_info),
    usecase: ListProjectMemberInvitationsUseCase = Depends(
        ListProjectMemberInvitationsUseCase
    ),
) -> SuccessResponse[CursorPage[ProjectMemberInvitationResponse]]:
    invitations = await usecase(
        project_id=project_id,
        user_id=user.user_id,
        status=status,
        limit=limit,
        cursor=cursor,
    )
    return SuccessResponse(
        message="프로젝트 초대 목록을 조회했습니다.",
        data=invitations,
    )


@router.post(
    "/{project_id}/member-invitations/{token}/accept",
    response_model=SuccessResponse[ProjectMemberResponse],
    status_code=200,
)
async def accept_project_member_invitation_endpoint(
    project_id: int,
    token: str,
    user: UserInfo = Depends(get_user_info),
    usecase: AcceptProjectMemberInvitationUseCase = Depends(
        AcceptProjectMemberInvitationUseCase
    ),
) -> SuccessResponse[ProjectMemberResponse]:
    member = await usecase(
        project_id=project_id,
        token=token,
        user_id=user.user_id,
    )
    return SuccessResponse(
        message="프로젝트 초대를 승인했습니다.",
        data=member,
    )


@router.delete(
    "/{project_id}/member-invitations/{invitation_id}",
    response_model=SuccessResponse[ProjectMemberInvitationResponse],
    status_code=200,
)
async def cancel_project_member_invitation_endpoint(
    project_id: int,
    invitation_id: int,
    user: UserInfo = Depends(get_user_info),
    usecase: CancelProjectMemberInvitationUseCase = Depends(
        CancelProjectMemberInvitationUseCase
    ),
) -> SuccessResponse[ProjectMemberInvitationResponse]:
    invitation = await usecase(
        project_id=project_id,
        invitation_id=invitation_id,
        user_id=user.user_id,
    )
    return SuccessResponse(
        message="프로젝트 초대를 취소했습니다.",
        data=invitation,
    )


@router.post(
    "/{project_id}/member-invitations/{invitation_id}/resend",
    response_model=SuccessResponse[ProjectMemberInvitationResponse],
    status_code=200,
)
async def resend_project_member_invitation_endpoint(
    project_id: int,
    invitation_id: int,
    user: UserInfo = Depends(get_user_info),
    usecase: ResendProjectMemberInvitationUseCase = Depends(
        ResendProjectMemberInvitationUseCase
    ),
) -> SuccessResponse[ProjectMemberInvitationResponse]:
    invitation = await usecase(
        project_id=project_id,
        invitation_id=invitation_id,
        user_id=user.user_id,
    )
    return SuccessResponse(
        message="프로젝트 초대 메일을 재발송했습니다.",
        data=invitation,
    )


@router.delete(
    "/{project_id}/members/{target_user_id}",
    response_model=SuccessResponse[ProjectMemberResponse],
    status_code=200,
)
async def remove_project_member_endpoint(
    project_id: int,
    target_user_id: int,
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
    project_id: int,
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
