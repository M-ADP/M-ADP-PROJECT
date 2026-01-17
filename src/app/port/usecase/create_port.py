from fastapi import Depends

from src.app.port.exceptions import PortAlreadyExists
from src.app.port.models import Port
from src.app.port.schemas import PortCreate
from src.app.project.exceptions import ProjectNotFound
from src.common.id_generator import generate_sonyflake_id
from src.core.usecase import BaseUseCase
from src.infra.db.uow import SQLAlchemyUnitOfWork
from src.api.deps.uow import get_uow


class CreatePortUseCase(BaseUseCase):
    """포트를 생성하는 유즈케이스"""

    def __init__(self, uow: SQLAlchemyUnitOfWork = Depends(get_uow)):
        super().__init__(uow)

    async def execute(
        self,
        project_id: str,
        request: PortCreate,
        user_id: str,
    ) -> Port:
        project = await self.uow.project.get_by_id_for_user(project_id, user_id)
        if project is None:
            raise ProjectNotFound()

        if await self.uow.port.exists_by_from_port(
            project_id,
            request.from_port,
            exclude_port_id=None,
        ):
            raise PortAlreadyExists()

        port_row = Port(
            id=generate_sonyflake_id(),
            project_id=project_id,
            from_ip=request.from_ip,
            from_port=request.from_port,
            port_number=request.port_number,
            protocol=request.protocol,
        )
        return await self.uow.port.insert(port_row)
