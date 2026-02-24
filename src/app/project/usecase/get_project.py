from fastapi import Depends

from src.app.project.exceptions import ProjectNotFound
from src.app.port.schemas import PortResponse
from src.app.project.schemas import DeploymentItem, MetricPoint, ProjectDetailResponse
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.project_resource import ProjectResourceClient
from src.core.client.deployment import DeploymentClient
from src.dependencies.uow import get_uow
from src.dependencies.client.project_resource import get_project_resource_client
from src.dependencies.client.deployment import get_deployment_client


class GetProjectUseCase(BaseUseCase):
    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        project_resource_client: ProjectResourceClient = Depends(get_project_resource_client),
        deployment_client: DeploymentClient = Depends(get_deployment_client),
    ):
        self.uow = uow
        self.project_resource_client = project_resource_client
        self.deployment_client = deployment_client

    async def __call__(
        self,
        project_id: int,
        user_id: str,
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

            ports = await self.uow.port.list_by_project(
                project_id=project_id,
                limit=100,
                cursor=None,
            )

            usage = await self.project_resource_client.get_usage(
                project=project,
                days=7,
                interval_minutes=60,
            )
            deployments = await self.deployment_client.list_by_project(project_id)

            return ProjectDetailResponse(
                id=project.id,
                name=project.name,
                my_role=my_role,
                deployments=[
                    DeploymentItem(
                        id=deployment.id,
                        name=deployment.name,
                        runtime=deployment.runtime,
                        pod_count=deployment.pod_count,
                        exposed_port=deployment.exposed_port,
                        cpu_usage_percent=deployment.cpu_usage_percent,
                        ram_usage_percent=deployment.ram_usage_percent,
                        health_status=deployment.health_status,
                    )
                    for deployment in deployments
                ],
                cpu_usage=[
                    MetricPoint(timestamp=point.timestamp, value=point.value)
                    for point in usage.cpu
                ],
                memory_usage=[
                    MetricPoint(timestamp=point.timestamp, value=point.value)
                    for point in usage.memory
                ],
                disk_usage=[
                    MetricPoint(timestamp=point.timestamp, value=point.value)
                    for point in usage.disk
                ],
                network_usage=[
                    MetricPoint(timestamp=point.timestamp, value=point.value)
                    for point in usage.network
                ],
                traffic_per_hour=[
                    MetricPoint(timestamp=point.timestamp, value=point.value)
                    for point in usage.traffic_per_hour
                ],
                ports=[PortResponse.model_validate(port) for port in ports],
            )
