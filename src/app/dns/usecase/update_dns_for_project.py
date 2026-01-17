from fastapi import Depends

from src.app.dns.models import DNS
from src.app.dns.schemas import DNSUpdate
from src.app.dns.exceptions import DNSNameAlreadyExists, DNSNotFound
from src.app.project.exceptions import ProjectNotFound
from src.core.usecase import BaseUseCase
from src.infra.db.uow import SQLAlchemyUnitOfWork
from src.api.deps.uow import get_uow

DNS_DOMAIN = "mdeveloper.platform"


class UpdateDNSForProjectUseCase(BaseUseCase):
    """프로젝트의 DNS 서브도메인을 업데이트하는 유즈케이스"""

    def __init__(self, uow: SQLAlchemyUnitOfWork = Depends(get_uow)):
        super().__init__(uow)

    async def execute(
        self,
        project_id: str,
        dns_id: str,
        request: DNSUpdate,
        user_id: str,
    ) -> DNS:
        project = await self.uow.project.get_by_id_for_user(project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        dns = await self.uow.dns.get_by_id_for_project(dns_id, project_id)
        if dns is None:
            raise DNSNotFound()

        # 새 DNS 이름 생성
        new_dns_name = f"{request.subdomain}.{DNS_DOMAIN}"

        # DNS 이름 중복 체크 (현재 DNS ID 제외)
        if await self.uow.dns.exists_by_dns_name(new_dns_name, exclude_dns_id=dns_id):
            raise DNSNameAlreadyExists()

        # DNS 이름 업데이트
        dns.dns_name = new_dns_name
        await self.uow.session.flush()

        return dns
