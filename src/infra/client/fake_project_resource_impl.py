from src.core.client.project_resource import ProjectResourceClient, ResourceUsageData
from src.core.domain.project import Project


class FakeProjectResourceClientImpl(ProjectResourceClient):

    async def create(self, user_id: int, role: str, project: Project) -> None:
        pass

    async def delete(self, user_id: int, role: str, project: Project) -> None:
        pass

    async def allocate(self, user_id: int, role: str, project: Project) -> None:
        pass

    async def get_usage(
        self,
        project: Project,
        days: int = 7,
        interval_minutes: int = 60,
    ) -> ResourceUsageData:
        return ResourceUsageData()
