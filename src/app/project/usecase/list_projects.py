from src.app.project.schemas import (
    DeploymentStatus,
    DeploymentSummary,
    ProjectListItemResponse,
)
from src.common.client.deployment_summary import DeploymentSummaryItem
from src.core.schemas import CursorPage
from src.core.usecase import BaseUseCase


class ListProjectsUseCase(BaseUseCase):
    _allowed_states = {"RUNNING", "STOPPED", "FAILED"}

    async def execute(
        self,
        user_id: str,
        limit: int,
        cursor: str | None = None,
    ) -> CursorPage[ProjectListItemResponse]:
        # 사용자가 멤버로 참여한 프로젝트 ID 목록 조회
        project_ids = await self.uow.project_member.list_project_ids_by_user(
            user_id=user_id,
            limit=limit + 1,
            cursor=cursor,
        )
        has_next = len(project_ids) > limit
        project_ids = project_ids[:limit]

        # 프로젝트 정보 조회
        projects = await self.uow.project.get_by_ids(project_ids)
        # ID 순서 유지
        project_map = {p.id: p for p in projects}
        ordered_projects = [project_map[pid] for pid in project_ids if pid in project_map]

        summary_map = await self._get_summary_map(project_ids)
        role_map = await self.uow.project_member.get_roles_batch(project_ids, user_id)

        return CursorPage(
            items=[
                await self._to_list_item(
                    project,
                    summary_map.get(project.id),
                    role_map.get(project.id, "VIEWER"),
                )
                for project in ordered_projects
            ],
            has_next=has_next,
        )

    async def _to_list_item(
        self,
        project,
        summary: DeploymentSummaryItem | None,
        my_role: str,
    ) -> ProjectListItemResponse:
        dns = await self.uow.dns.get_by_project(project.id)
        summary_item = summary or DeploymentSummaryItem(project_id=project.id)
        state = (
            summary_item.state
            if summary_item.state in self._allowed_states
            else "FAILED"
        )
        return ProjectListItemResponse(
            id=project.id,
            name=project.name,
            my_role=my_role,
            domain=dns.dns_name if dns else None,
            deployment_summary=DeploymentSummary(
                running=summary_item.running,
                warning=summary_item.warning,
            ),
            deployment_status=DeploymentStatus(
                state=state,
                message=summary_item.message,
            ),
        )

    async def _get_summary_map(
        self,
        project_ids: list[str],
    ) -> dict[str, DeploymentSummaryItem]:
        if not project_ids:
            return {}
        summaries = await self.deployment_summary_client.get_summary_batch(
            project_ids=project_ids,
        )
        return {summary.project_id: summary for summary in summaries}
