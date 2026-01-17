from fastapi import Depends

from src.api.deps.uow import get_uow
from src.core.uow import UnitOfWork


class BaseUseCase:
    def __init__(
            self,
            uow : UnitOfWork = Depends(get_uow)
    ):
        self.uow = uow