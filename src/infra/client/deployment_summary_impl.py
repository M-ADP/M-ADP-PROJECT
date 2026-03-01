from src.core.client.deployment_summary import (
    DeploymentSummaryClient,
    DeploymentSummaryItem,
)


class MockDeploymentSummaryClient(DeploymentSummaryClient):
    """배포 요약 정보 접근 Mock 클라이언트"""

    async def get_summary_batch(
        self,
        project_ids: list[int],
    ) -> list[DeploymentSummaryItem]:
        return [
            DeploymentSummaryItem(
                project_id=project_id,
                running=0,
                warning=0,
                state="STOPPED",
                message="프로젝트가 현재 중지 상태입니다.",
            )
            for project_id in project_ids
        ]
