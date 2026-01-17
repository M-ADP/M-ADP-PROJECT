from fastapi import APIRouter, Depends

from src.app.dns.schemas import DNSCreate, DNSPortBinding, DNSResponse, DNSUpdate
from src.app.dns.usecase import (
    CreateDNSForProjectUseCase,
    GetDNSForProjectUseCase,
    DeleteDNSFromProjectUseCase,
    UpdateDNSForProjectUseCase,
    BindPortToDNSUseCase,
)
from src.api.deps.auth import UserInfo, get_user_info
from src.core.schemas import SuccessResponse

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
    usecase: CreateDNSForProjectUseCase = Depends(CreateDNSForProjectUseCase),
) -> SuccessResponse[DNSResponse]:
    """프로젝트에 DNS를 생성합니다."""
    dns = await usecase(project_id, payload, user_id=user.user_id)
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
    usecase: GetDNSForProjectUseCase = Depends(GetDNSForProjectUseCase),
) -> SuccessResponse[DNSResponse | None]:
    """프로젝트의 DNS를 조회합니다."""
    dns = await usecase(project_id, user_id=user.user_id)
    
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
    usecase: DeleteDNSFromProjectUseCase = Depends(DeleteDNSFromProjectUseCase),
) -> SuccessResponse[DNSResponse]:
    """프로젝트의 DNS를 삭제합니다."""
    dns = await usecase(project_id, dns_id, user_id=user.user_id)
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
    usecase: UpdateDNSForProjectUseCase = Depends(UpdateDNSForProjectUseCase),
) -> SuccessResponse[DNSResponse]:
    """프로젝트의 DNS 서브도메인을 업데이트합니다."""
    dns = await usecase(project_id, dns_id, payload, user_id=user.user_id)
    return SuccessResponse(
        message="DNS가 업데이트되었습니다.",
        data=DNSResponse.model_validate(dns),
    )


@router.patch(
    "/{project_id}/dns-records/{dns_id}/port",
    response_model=SuccessResponse[DNSResponse],
    status_code=200,
)
async def bind_port_to_dns_endpoint(
    project_id: str,
    dns_id: str,
    payload: DNSPortBinding,
    user: UserInfo = Depends(get_user_info),
    usecase: BindPortToDNSUseCase = Depends(BindPortToDNSUseCase),
) -> SuccessResponse[DNSResponse]:
    """DNS에 포트를 바인딩합니다."""
    dns = await usecase(project_id, dns_id, payload, user_id=user.user_id)
    return SuccessResponse(
        message="DNS에 포트가 바인딩되었습니다.",
        data=DNSResponse.model_validate(dns),
    )
