from fastapi import Depends

from src.app.port.exceptions import PortAlreadyExists, PortNotFound
from src.app.port.models import Port
from src.app.port.schemas import PortUpdate
from src.app.project.exceptions import ProjectNotFound
from src.core.usecase import BaseUseCase
from src.infra.db.uow import SQLAlchemyUnitOfWork
from src.api.deps.uow import get_uow


class UpdatePortUseCase(BaseUseCase):
    """포트를 업데이트하는 유즈케이스"""

    def __init__(self, uow: SQLAlchemyUnitOfWork = Depends(get_uow)):
        super().__init__(uow)

    async def execute(
        self,
        project_id: str,
        port_id: str,
        request: PortUpdate,
        user_id: str,
    ) -> Port:
        project = await self.uow.project.get_by_id_for_user(project_id, user_id)
        if project is None:
            raise ProjectNotFound()

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

        port.update(
            from_ip=request.from_ip,
            from_port=request.from_port,
            port_number=request.port_number,
            protocol=request.protocol
        )
        await self.uow.session.flush()
        return port
