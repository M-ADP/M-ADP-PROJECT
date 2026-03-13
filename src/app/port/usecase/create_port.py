from fastapi import Depends

from src.app.port.exceptions import PortAlreadyExists, PortCreationFailed
from src.core.exceptions import ResourceServerException
from src.core.domain.port import Port
from src.app.port.schemas import PortCreate
from src.app.project.exceptions import ProjectNotFound, OnlyOwnerCanManagePorts
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.project_resource import ProjectResourceClient
from src.dependencies.uow import get_uow
from src.dependencies.client.project_resource import get_project_resource_client


class CreatePortUseCase(BaseUseCase):
    """포트를 생성하는 유즈케이스"""

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
        request: PortCreate,
        user_id: int,
        role: str,
    ) -> Port:
        async with self.uow:
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                raise OnlyOwnerCanManagePorts()

            # 신규 Port 객체 생성 (port_id 선발급)
            port_row = Port(
                project_id=project_id,
                target_deployment_name=request.target_deployment_name,
                port=request.port,
                target_port=request.target_port,
                protocol=request.protocol,
                service_type=request.service_type,
            )
            # 프로젝트 ID와 발급된 Port ID를 조합하여 service_id 자동 생성
            port_row.service_id = f"svc-{project_id}-{port_row.id}"
            port_row.service_name = port_row.service_id

            if await self.uow.port.exists_by_service_id(
                project_id,
                port_row.service_id,
                exclude_port_id=None,
            ):
                raise PortAlreadyExists()

            port = await self.uow.port.insert(port_row)
            try:
                await self.project_resource_client.open_port(
                    user_id=user_id,
                    role=role,
                    project=project,
                    port=port,
                )
            except ResourceServerException as e:
                raise PortCreationFailed() from e
            return port
