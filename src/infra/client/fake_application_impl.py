from src.core.client.application import ApplicationClient, ApplicationItemData, DeploymentSummaryItem


class FakeApplicationClientImpl(ApplicationClient):

    async def list_by_project(
        self,
        project_id: int,
        user_id: int,
        role: str,
    ) -> list[ApplicationItemData]:
        return []

    async def get_summary_batch(
        self,
        project_ids: list[int],
        user_id: int,
        role: str,
    ) -> list[DeploymentSummaryItem]:
        return []
