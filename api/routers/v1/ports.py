from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps.auth import UserInfo, get_user_info
from api.deps.db import get_db_session
from app.port.schemas import PortCreate, PortResponse
from app.port.service import create_port, delete_port, list_ports
from core.schemas import CursorPage, SuccessResponse

router = APIRouter(prefix="/projects/{project_id}/ports", tags=["project-ports"])


@router.post(
    "",
    response_model=SuccessResponse[PortResponse],
    status_code=201,
)
async def create_project_port_endpoint(
    project_id: str,
    payload: PortCreate,
    user: UserInfo = Depends(get_user_info),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[PortResponse]:
    async with session.begin():
        port = await create_port(
            project_id=project_id,
            request=payload,
            user_id=user.user_id,
            session=session,
        )
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
    project_id: str,
    cursor: str | None = Query(
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
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[CursorPage[PortResponse]]:
    ports = await list_ports(
        project_id=project_id,
        user_id=user.user_id,
        session=session,
        limit=limit,
        cursor=cursor,
    )
    return SuccessResponse(
        message="포트 목록을 조회했습니다.",
        data=ports,
    )


@router.delete(
    "/{port_id}",
    response_model=SuccessResponse[PortResponse],
    status_code=200,
)
async def delete_project_port_endpoint(
    project_id: str,
    port_id: str,
    user: UserInfo = Depends(get_user_info),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[PortResponse]:
    async with session.begin():
        port = await delete_port(
            project_id=project_id,
            port_id=port_id,
            user_id=user.user_id,
            session=session,
        )
    return SuccessResponse(
        message="포트가 삭제되었습니다.",
        data=PortResponse.model_validate(port),
    )
