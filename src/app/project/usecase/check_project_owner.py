import logging
from fastapi import Depends

from src.app.base_usecase import BaseUseCase

logger = logging.getLogger(__name__)
from src.core.uow import UnitOfWork
from src.dependencies.uow import get_uow


class CheckProjectOwnerUseCase(BaseUseCase):
    """특정 사용자가 프로젝트의 소유자(OWNER)인지 확인합니다."""

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
    ):
        self.uow = uow

    async def __call__(
        self,
        project_id: int,
        user_id: int,
    ) -> bool:
        logger.error(f"[CHECK_OWNER] project_id={project_id!r} user_id={user_id!r}")  # 임시
        async with self.uow:
            result = await self.uow.project_member.is_owner(
                project_id=project_id,
                user_id=user_id,
            )
            logger.error(f"[CHECK_OWNER] is_owner={result} project_id={project_id!r} user_id={user_id!r}")  # 임시
            return result
