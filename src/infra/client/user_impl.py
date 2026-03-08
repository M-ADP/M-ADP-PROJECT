import logging
from enum import Enum

from src.common.config.user_server import UserServerConfig

logger = logging.getLogger(__name__)
from src.core.client.http import HttpClient
from src.core.client.user import UserClient, UserInfo
from src.infra.client.asyncio_http import AioHttpClient


class UserAPIUrls(str, Enum):
    GET_USER_BY_ID = "/user/profile/id/{user_id}"


class UserClientImpl(UserClient):
    """사용자 서비스 클라이언트 구현체"""

    def __init__(
        self,
        user_server_config: UserServerConfig,
        http_client: HttpClient | None = None,
    ):
        self.base_url = user_server_config.SERVER_BASE_URL
        self.http_client = http_client or AioHttpClient(base_url=self.base_url)

    async def get_user(self, user_id: int) -> UserInfo | None:
        url = UserAPIUrls.GET_USER_BY_ID.format(user_id=user_id)
        logger.error(f"[GET_USER] 요청: url={self.base_url + url} user_id={user_id!r}")  # 임시
        response = await self.http_client.get(url)
        try:
            logger.error(f"[GET_USER] 응답: status={response.status} user_id={user_id!r}")  # 임시
            if response.status != 200:
                return None

            payload = await response.json(content_type=None)
            logger.error(f"[GET_USER] payload={payload!r}")  # 임시
            return UserInfo(
                user_id=str(payload.get("user_id")),
                username=str(payload.get("nickname")),
                profile_image=payload.get("profile") or None,
            )
        except Exception as e:
            logger.error(f"[GET_USER] 예외: {e!r} user_id={user_id!r}")  # 임시
            return None
        finally:
            response.release()

    async def exists(self, user_id: int) -> bool:
        response = await self.http_client.get(
            UserAPIUrls.GET_USER_BY_ID.format(user_id=user_id)
        )
        try:
            return response.status == 200
        finally:
            response.release()
