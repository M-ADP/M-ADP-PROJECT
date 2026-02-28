from fastapi import Depends

from src.core.domain.dns import DNS
from src.app.project.exceptions import ProjectNotFound
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.dependencies.uow import get_uow


class GetDNSForProjectUseCase(BaseUseCase):
    """프로젝트의 DNS를 조회하는 유즈케이스"""

    def __init__(self, uow: UnitOfWork = Depends(get_uow)):
        self.uow = uow

    async def __call__(
        self,
        project_id: int,
        user_id: int,
    ) -> DNS | None:
        async with self.uow:
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            has_access = await self.uow.project_member.has_access(project_id, user_id)
            if not has_access:
                raise ProjectNotFound()

            dns = await self.uow.dns.get_by_project(project_id)
            return dns
