from fastapi import Depends

from src.app.project.exceptions import ProjectNotFound
from src.app.project.schemas import (
    ApplicationItem,
    ProjectDetailResponse,
    ProjectResourceSnapshot,
    ResourceMetricSnapshot,
    ResourceSnapshot,
)
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.project_resource import ProjectResourceClient
from src.core.client.application import ApplicationClient
from src.dependencies.uow import get_uow
from src.dependencies.client.project_resource import get_project_resource_client
from src.dependencies.client.application import get_deployment_client


class GetProjectUseCase(BaseUseCase):
    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        project_resource_client: ProjectResourceClient = Depends(get_project_resource_client),
        deployment_client: ApplicationClient = Depends(get_deployment_client),
    ):
        self.uow = uow
        self.project_resource_client = project_resource_client
        self.deployment_client = deployment_client

    async def __call__(
        self,
        project_id: int,
        user_id: int,
        role: str,
    ) -> ProjectDetailResponse:
        async with self.uow:
            # 프로젝트 존재 여부 확인
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            # 멤버 기반 접근 권한 및 역할 확인
            my_role = await self.uow.project_member.get_role(project_id, user_id)
            if my_role is None:
                raise ProjectNotFound()

            usage = await self.project_resource_client.get_usage(
                project=project,
                user_id=user_id,
                days=7,
                interval_minutes=60,
            )
            deployments = await self.deployment_client.list_by_project(project_id, user_id=user_id, role=role)

            return ProjectDetailResponse(
                id=project.id,
                name=project.name,
                my_role=my_role,
                deployments=[
                    ApplicationItem(
                        id=deployment.id,
                        name=deployment.name,
                        pod_count=deployment.pod_count,
                        exposed_port=deployment.exposed_port,
                        cpu_usage_percent=deployment.cpu_usage_percent,
                        ram_usage_percent=deployment.ram_usage_percent,
                        health_status=deployment.health_status,
                    )
                    for deployment in deployments
                ],
                resource=ProjectResourceSnapshot(
                    project_id=usage.project_id,
                    cpu=ResourceMetricSnapshot(
                        limit=usage.cpu.limit,
                        used=usage.cpu.used,
                        percentage=usage.cpu.percentage,
                        unit=usage.cpu.unit,
                    ),
                    memory=ResourceMetricSnapshot(
                        limit=usage.memory.limit,
                        used=usage.memory.used,
                        percentage=usage.memory.percentage,
                        unit=usage.memory.unit,
                    ),
                    disk=ResourceMetricSnapshot(
                        limit=usage.disk.limit,
                        used=usage.disk.used,
                        percentage=usage.disk.percentage,
                        unit=usage.disk.unit,
                    ),
                    instance=ResourceSnapshot(
                        limit=usage.instance.limit,
                        used=usage.instance.used,
                        percentage=usage.instance.percentage,
                    ),
                ),
            )
