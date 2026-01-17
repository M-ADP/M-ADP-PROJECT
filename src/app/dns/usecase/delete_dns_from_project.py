from fastapi import Depends

from src.app.dns.models import DNS
from src.app.dns.exceptions import DNSNotFound
from src.app.project.exceptions import ProjectNotFound
from src.core.usecase import BaseUseCase
from src.infra.db.uow import SQLAlchemyUnitOfWork
from src.api.deps.uow import get_uow


class DeleteDNSFromProjectUseCase(BaseUseCase):
    """프로젝트의 DNS를 삭제하는 유즈케이스"""

    def __init__(self, uow: SQLAlchemyUnitOfWork = Depends(get_uow)):
        super().__init__(uow)

    async def execute(
        self,
        project_id: str,
        dns_id: str,
        user_id: str,
    ) -> DNS:
        project = await self.uow.project.get_by_id_for_user(project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        dns = await self.uow.dns.get_by_id_for_project(dns_id, project_id)
        if dns is None:
            raise DNSNotFound()

        # DNS 삭제
        await self.uow.dns.delete(dns)

        return dns
