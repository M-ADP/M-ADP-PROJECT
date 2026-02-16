from src.app.port.exceptions import PortAlreadyExists
from src.app.port.model import Port
from src.app.port.schemas import PortCreate
from src.app.project.exceptions import ProjectNotFound, OnlyOwnerCanManagePorts
from src.core.usecase import BaseUseCase


class CreatePortUseCase(BaseUseCase):
    """포트를 생성하는 유즈케이스"""

    async def execute(
        self,
        project_id: str,
        request: PortCreate,
        user_id: str,
    ) -> Port:
        project = await self.uow.project.get_by_id(project_id)
        if project is None:
            raise ProjectNotFound()

        is_owner = await self.uow.project_member.is_owner(project_id, user_id)
        if not is_owner:
            raise OnlyOwnerCanManagePorts()

        if await self.uow.port.exists_by_from_port(
            project_id,
            request.from_port,
            exclude_port_id=None,
        ):
            raise PortAlreadyExists()

        port_row = Port(
            project_id=project_id,
            from_ip=request.from_ip,
            from_port=request.from_port,
            port_number=request.port_number,
            protocol=request.protocol,
        )
        port = await self.uow.port.insert(port_row)
        await self.project_resource_client.open_port(
            user_id=user_id,
            project=project,
            port=port,
        )
        return port
