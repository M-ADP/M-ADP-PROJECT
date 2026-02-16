from src.app.project.exceptions import ProjectNotFound
from src.app.port.schemas import PortResponse
from src.app.project.schemas import DeploymentItem, MetricPoint, ProjectDetailResponse
from src.core.usecase import BaseUseCase


class GetProjectUseCase(BaseUseCase):
    async def execute(
        self,
        project_id: str,
        user_id: str,
    ) -> ProjectDetailResponse:
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
