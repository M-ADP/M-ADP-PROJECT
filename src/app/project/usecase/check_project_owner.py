from fastapi import Depends

from src.app.base_usecase import BaseUseCase
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
        async with self.uow:
            result = await self.uow.project_member.is_owner(
                project_id=project_id,
                user_id=user_id,
            )
            return result
