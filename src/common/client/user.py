from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class UserInfo:
    user_id: str
    username: str
    profile_image: str | None = None


class UserClient(ABC):
    @abstractmethod
    async def get_user(self, user_id: str) -> UserInfo | None:
        """사용자 정보를 조회합니다. 존재하지 않으면 None 반환."""
        ...

    @abstractmethod
    async def exists(self, user_id: str) -> bool:
        """사용자 존재 여부를 확인합니다."""
        ...
