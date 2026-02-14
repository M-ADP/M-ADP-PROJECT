from src.app.port.exceptions import PortNotFound
from src.app.port.model import Port
from src.app.project.exceptions import ProjectNotFound, OnlyOwnerCanManagePorts
from src.core.usecase import BaseUseCase


class DeletePortUseCase(BaseUseCase):
    """포트를 삭제하는 유즈케이스"""

    async def execute(
        self,
        project_id: str,
        port_id: str,
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

        await self.project_resource_client.close_port(
            user_id=user_id,
            name=project.name,
            port_id=str(port.from_port)
        )
        await self.uow.port.delete(port)
        return port
