from fastapi import Depends

from src.app.port.exceptions import PortNotFound
from src.app.port.models import Port
from src.app.project.exceptions import ProjectNotFound
from src.core.usecase import BaseUseCase
from src.infra.db.uow import SQLAlchemyUnitOfWork
from src.api.deps.uow import get_uow


class DeletePortUseCase(BaseUseCase):
    """포트를 삭제하는 유즈케이스"""

    def __init__(self, uow: SQLAlchemyUnitOfWork = Depends(get_uow)):
        super().__init__(uow)

    async def execute(
        self,
        project_id: str,
        port_id: str,
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

        await self.uow.port.delete(port)
        return port
