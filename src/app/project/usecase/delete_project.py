import logging

from fastapi import Depends

from src.app.project.exceptions import (
    ProjectNotFound,
    OnlyOwnerCanDeleteProject,
    ProjectDeletionFailed,
)
from src.core.domain.project import Project
from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.core.client.application import ApplicationClient
from src.core.client.dns import DnsClient
from src.core.exceptions import ApplicationServerException, DnsServerException
from src.dependencies.uow import get_uow
from src.dependencies.client.application import get_deployment_client
from src.dependencies.client.dns import get_dns_client

logger = logging.getLogger(__name__)


class DeleteProjectUseCase(BaseUseCase):
    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
        deployment_client: ApplicationClient = Depends(get_deployment_client),
        dns_client: DnsClient = Depends(get_dns_client),
    ):
        self.uow = uow
        self.deployment_client = deployment_client
        self.dns_client = dns_client

    async def __call__(
        self,
        project_id: int,
        user_id: int,
        role: str,
    ) -> Project:
        async with self.uow:
            project = await self.uow.project.get_by_id(project_id)
            if project is None:
                raise ProjectNotFound()

            is_owner = await self.uow.project_member.is_owner(project_id, user_id)
            if not is_owner:
                raise OnlyOwnerCanDeleteProject()

            logger.info(
                "[DeleteProjectUseCase] app-deployment 삭제 시작: project_id=%s",
                project_id,
            )
            try:
                await self.deployment_client.delete_by_project(
                    project_id=project_id,
                    user_id=user_id,
                    role=role,
                )
                logger.info(
                    "[DeleteProjectUseCase] app-deployment 삭제 성공: project_id=%s, result=204",
                    project_id,
                )
            except ApplicationServerException as exc:
                logger.warning(
                    "[DeleteProjectUseCase] app-deployment 삭제 실패: project_id=%s, result=%s",
                    project_id,
                    str(exc),
                )
                raise ProjectDeletionFailed() from exc

            logger.info(
                "[DeleteProjectUseCase] DNS 삭제 시작: project_id=%s",
                project_id,
            )
            try:
                await self.dns_client.delete_by_project(
                    project_id=project_id,
                    user_id=user_id,
                    role=role,
                )
                logger.info(
                    "[DeleteProjectUseCase] DNS 삭제 성공: project_id=%s",
                    project_id,
                )
            except DnsServerException as exc:
                logger.warning(
                    "[DeleteProjectUseCase] DNS 삭제 실패: project_id=%s, result=%s",
                    project_id,
                    str(exc),
                )
                # DNS 삭제 실패가 전체 프로젝트 삭제를 막아야 하는지는 정책에 따라 다를 수 있습니다.
                # 여기서는 앱 배포 삭제와 마찬가지로 실패 시 예외를 던지도록 합니다.
                raise ProjectDeletionFailed() from exc

            logger.info(
                "[DeleteProjectUseCase] 프로젝트 DB 삭제 시작: project_id=%s",
                project_id,
            )
            await self.uow.project.delete(project)
            logger.info(
                "[DeleteProjectUseCase] 프로젝트 DB 삭제 완료: project_id=%s",
                project_id,
            )
            return project
