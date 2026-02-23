from fastapi import Depends

from src.app.base_usecase import BaseUseCase
from src.core.uow import UnitOfWork
from src.dependencies.uow import get_uow


class CheckProjectAvailableUseCase(BaseUseCase):
    """요청 사용자의 프로젝트 접근 가능 여부(멤버 여부)를 확인합니다."""

    def __init__(
        self,
        uow: UnitOfWork = Depends(get_uow),
    ):
        self.uow = uow

    async def __call__(
        self,
        project_id: str,
        user_id: str,
    ) -> bool:
        async with self.uow:
            return await self.uow.project_member.has_access(
                project_id=project_id,
                user_id=user_id,
            )
