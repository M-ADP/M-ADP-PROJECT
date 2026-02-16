from fastapi import Depends

from src.app.port.exceptions import PortAlreadyExists, PortNotFound
from src.core.domain.port import Port
from src.app.port.schemas import PortUpdate
from src.app.project.exceptions import ProjectNotFound, OnlyOwnerCanManagePorts
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.project_resource import ProjectResourceClient
from src.dependencies.uow import get_uow
from src.dependencies.client.project_resource import get_project_resource_client


class UpdatePortUseCase(BaseUseCase):
    """포트를 업데이트하는 유즈케이스"""

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        project_resource_client: ProjectResourceClient = Depends(get_project_resource_client),
    ):
        self.uow = uow
        self.project_resource_client = project_resource_client

    async def __call__(
        self,
        project_id: str,
        port_id: str,
        request: PortUpdate,
        user_id: str,
    ) -> Port:
        async with self.uow:
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                raise OnlyOwnerCanManagePorts()

            
            original_port = await self.uow.port.get_by_id_for_project(
                project_id=project_id,
                port_id=port_id,
            )
            if original_port is None:
                raise PortNotFound()

            if await self.uow.port.exists_by_from_port(
                project_id,
                request.from_port,
                exclude_port_id=port_id,
            ):
                raise PortAlreadyExists()

            port = await self.uow.port.update(
                project_id=project_id,
                port_id=port_id,
                from_ip=request.from_ip,
                from_port=request.from_port,
                port_number=request.port_number,
                protocol=request.protocol,
            )
            await self.project_resource_client.update_port(
                user_id=user_id,
                project=project,
                original_port=original_port,
                updated_port=port,
            )
            return port
