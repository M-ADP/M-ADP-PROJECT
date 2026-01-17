from fastapi import Depends

from src.app.dns.models import DNS
from src.app.project.exceptions import ProjectNotFound
from src.core.usecase import BaseUseCase
from src.infra.db.uow import SQLAlchemyUnitOfWork
from src.api.deps.uow import get_uow


class GetDNSForProjectUseCase(BaseUseCase):
    """프로젝트의 DNS를 조회하는 유즈케이스"""

    def __init__(self, uow: SQLAlchemyUnitOfWork = Depends(get_uow)):
        super().__init__(uow)

    async def execute(
        self,
        project_id: str,
        user_id: str,
    ) -> DNS | None:
        project = await self.uow.project.get_by_id_for_user(project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        dns = await self.uow.dns.get_by_project(project_id)
        return dns
