from fastapi import APIRouter, Depends, Query

from src.dependencies.auth import UserInfo, get_user_info
from src.app.port.schemas import PortCreate, PortResponse, PortUpdate
from src.app.port.usecase import (
    CreatePortUseCase,
    ListPortsUseCase,
    UpdatePortUseCase,
    DeletePortUseCase,
)
from src.common.schemas import CursorPage, SuccessResponse

router = APIRouter(prefix="/projects/{project_id}/ports", tags=["project-ports"])


@router.post(
    "",
    response_model=SuccessResponse[PortResponse],
    status_code=201,
)
async def create_project_port_endpoint(
    project_id: int,
    payload: PortCreate,
    user: UserInfo = Depends(get_user_info),
    usecase: CreatePortUseCase = Depends(CreatePortUseCase),
) -> SuccessResponse[PortResponse]:
    port = await usecase(project_id=project_id, request=payload, user_id=user.user_id, role=user.role)
    return SuccessResponse(
        message="포트가 공개되었습니다.",
        data=PortResponse.model_validate(port),
    )


@router.get(
    "",
    response_model=SuccessResponse[CursorPage[PortResponse]],
    status_code=200,
)
async def list_project_ports_endpoint(
    project_id: int,
    cursor: int | None = Query(
        None,
        description="다음 페이지 커서(id). 지정하면 해당 커서 이후부터 조회",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="한 번에 가져올 포트 수 (1~100, 기본 20)",
    ),
    user: UserInfo = Depends(get_user_info),
    usecase: ListPortsUseCase = Depends(ListPortsUseCase),
) -> SuccessResponse[CursorPage[PortResponse]]:
    ports = await usecase(
        project_id=project_id,
        user_id=user.user_id,
        limit=limit,
        cursor=cursor,
    )
    return SuccessResponse(
        message="포트 목록을 조회했습니다.",
        data=ports,
    )


@router.put(
    "/{port_id}",
    response_model=SuccessResponse[PortResponse],
    status_code=200,
)
async def update_project_port_endpoint(
    project_id: int,
    port_id: int,
    payload: PortUpdate,
    user: UserInfo = Depends(get_user_info),
    usecase: UpdatePortUseCase = Depends(UpdatePortUseCase),
) -> SuccessResponse[PortResponse]:
    port = await usecase(
        project_id=project_id,
        port_id=port_id,
        request=payload,
        user_id=user.user_id,
        role=user.role,
    )
    return SuccessResponse(
        message="포트가 수정되었습니다.",
        data=PortResponse.model_validate(port),
    )


@router.delete(
    "/{port_id}",
    response_model=SuccessResponse[PortResponse],
    status_code=200,
)
async def delete_project_port_endpoint(
    project_id: int,
    port_id: int,
    user: UserInfo = Depends(get_user_info),
    usecase: DeletePortUseCase = Depends(DeletePortUseCase),
) -> SuccessResponse[PortResponse]:
    port = await usecase(project_id=project_id, port_id=port_id, user_id=user.user_id, role=user.role)
    return SuccessResponse(
        message="포트가 삭제되었습니다.",
        data=PortResponse.model_validate(port),
    )
