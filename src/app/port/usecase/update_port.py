from src.app.port.exceptions import PortAlreadyExists, PortNotFound
from src.app.port.model import Port
from src.app.port.schemas import PortUpdate
from src.app.project.exceptions import ProjectNotFound, OnlyOwnerCanManagePorts
from src.core.usecase import BaseUseCase


class UpdatePortUseCase(BaseUseCase):
    """포트를 업데이트하는 유즈케이스"""

    async def execute(
        self,
        project_id: str,
        port_id: str,
        request: PortUpdate,
        user_id: str,
    ) -> Port:
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
        await self.project_resource_client.update_port()
        return port
