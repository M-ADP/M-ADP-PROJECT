from src.common.client.deployment import DeploymentClient, DeploymentItemData


class MockDeploymentClient(DeploymentClient):
    """앱 배포 정보 접근 Mock 클라이언트"""

    async def list_by_project(
        self,
        project_id: str,
    ) -> list[DeploymentItemData]:
        return []
