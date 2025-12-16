from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dns.schemas import DNSCreate, DNSResponse, DNSUpdate
from app.dns.service import (
    create_dns_for_project,
    delete_dns_from_project,
    get_dns_for_project,
    update_dns_for_project,
)
from api.deps.auth import UserInfo, get_user_info
from api.deps.db import get_db_session
from core.schemas import SuccessResponse

router = APIRouter(prefix="/projects", tags=["dns"])


@router.post(
    "/{project_id}/dns",
    response_model=SuccessResponse[DNSResponse],
    status_code=201,
)
async def create_dns_endpoint(
    project_id: str,
    payload: DNSCreate,
    user: UserInfo = Depends(get_user_info),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[DNSResponse]:
    """프로젝트에 DNS를 생성합니다."""
    async with session.begin():
        dns = await create_dns_for_project(
            project_id,
            payload,
            user_id=user.user_id,
            session=session,
        )
    return SuccessResponse(
        message="DNS가 생성되었습니다.",
        data=DNSResponse.model_validate(dns),
    )


@router.get(
    "/{project_id}/dns-records",
    response_model=SuccessResponse[DNSResponse | None],
    status_code=200,
)
async def get_dns_endpoint(
    project_id: str,
    user: UserInfo = Depends(get_user_info),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[DNSResponse | None]:
    """프로젝트의 DNS를 조회합니다."""
    async with session.begin():
        dns = await get_dns_for_project(
            project_id,
            user_id=user.user_id,
            session=session,
        )
    
    data = DNSResponse.model_validate(dns) if dns else None
    return SuccessResponse(
        message="DNS를 조회했습니다.",
        data=data,
    )


@router.delete(
    "/{project_id}/dns-records/{dns_id}",
    response_model=SuccessResponse[DNSResponse],
    status_code=200,
)
async def delete_dns_endpoint(
    project_id: str,
    dns_id: str,
    user: UserInfo = Depends(get_user_info),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[DNSResponse]:
    """프로젝트의 DNS를 삭제합니다."""
    async with session.begin():
        dns = await delete_dns_from_project(
            project_id,
            dns_id,
            user_id=user.user_id,
            session=session,
        )
    return SuccessResponse(
        message="DNS가 삭제되었습니다.",
        data=DNSResponse.model_validate(dns),
    )


@router.patch(
    "/{project_id}/dns-records/{dns_id}",
    response_model=SuccessResponse[DNSResponse],
    status_code=200,
)
async def update_dns_endpoint(
    project_id: str,
    dns_id: str,
    payload: DNSUpdate,
    user: UserInfo = Depends(get_user_info),
    session: AsyncSession = Depends(get_db_session),
) -> SuccessResponse[DNSResponse]:
    """프로젝트의 DNS 서브도메인을 업데이트합니다."""
    async with session.begin():
        dns = await update_dns_for_project(
            project_id,
            dns_id,
            payload,
            user_id=user.user_id,
            session=session,
        )
    return SuccessResponse(
        message="DNS가 업데이트되었습니다.",
        data=DNSResponse.model_validate(dns),
    )
