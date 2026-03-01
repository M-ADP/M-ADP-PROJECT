from src.core.client.application import ApplicationClient, ApplicationItemData


class MockApplicationClient(ApplicationClient):
    """앱 배포 정보 접근 Mock 클라이언트"""

    async def list_by_project(
        self,
        project_id: int,
    ) -> list[ApplicationItemData]:
        return []
