from src.core.client.project_resource import (
    ProjectResourceClient,
    ProjectResourceSnapshotData,
    ResourceMetricSnapshotData,
    ResourceSnapshotData,
)
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
    ) -> ProjectResourceSnapshotData:
        return ProjectResourceSnapshotData(
            project_id=str(project.id),
            cpu=ResourceMetricSnapshotData(limit="0", used="0", percentage=0, unit=""),
            memory=ResourceMetricSnapshotData(limit="0", used="0", percentage=0, unit=""),
            disk=ResourceMetricSnapshotData(limit="0", used="0", percentage=0, unit=""),
            instance=ResourceSnapshotData(limit=0, used=0, percentage=0),
        )
