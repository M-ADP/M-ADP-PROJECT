from fastapi import Depends

from src.app.port.exceptions import PortNotFound
from src.core.domain.port import Port
from src.app.project.exceptions import ProjectNotFound, OnlyOwnerCanManagePorts
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.project_resource import ProjectResourceClient
from src.dependencies.uow import get_uow
from src.dependencies.client.project_resource import get_project_resource_client


class DeletePortUseCase(BaseUseCase):
    """포트를 삭제하는 유즈케이스"""

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        project_resource_client: ProjectResourceClient = Depends(get_project_resource_client),
    ):
        self.uow = uow
        self.project_resource_client = project_resource_client

    async def __call__(
        self,
        project_id: int,
        port_id: int,
        user_id: int,
    ) -> Port:
        async with self.uow:
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                raise OnlyOwnerCanManagePorts()

            port = await self.uow.port.get_by_id_for_project(
                project_id=project_id,
                port_id=port_id,
            )
            if port is None:
                raise PortNotFound()

            await self.project_resource_client.close_port(project=project, port=port)
            await self.uow.port.delete(port)
            return port
