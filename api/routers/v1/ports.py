from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps.auth import UserInfo, get_user_info
from api.deps.db import get_db_session
from app.port.schemas import PortCreate, PortResponse
from app.port.service import create_port
from core.schemas import SuccessResponse

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
