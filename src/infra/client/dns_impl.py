import logging
from enum import Enum

from src.core.client.http import HttpClient
from src.core.client.dns import DnsClient
from src.core.exceptions import DnsServerException
from src.common.config.dns_server import DnsServerConfig
from src.infra.client.asyncio_http import AioHttpClient

logger = logging.getLogger(__name__)


class DnsAPIUrls(str, Enum):
    DELETE_PROJECT_DNS = "/dns/project/{project_id}"


class DnsClientImpl(DnsClient):
    def __init__(
        self,
        dns_server_config: DnsServerConfig,
        http_client: HttpClient = AioHttpClient(),
    ):
        self.base_url = dns_server_config.SERVER_BASE_URL
        self.http_client = http_client

    async def delete_by_project(
        self,
        project_id: int,
        user_id: int,
        role: str,
    ) -> None:
        try:
            response = await self.http_client.delete(
                self.base_url + DnsAPIUrls.DELETE_PROJECT_DNS.format(
                    project_id=project_id
                ),
                headers={
                    "X-User-Id": str(user_id),
                    "X-User-Role": role,
                },
            )
        except Exception as e:
            logger.error("[DnsClientImpl] DNS 삭제 요청 실패: %s", str(e))
            raise DnsServerException() from e

        try:
            if not response.ok:
                logger.error(
                    "[DnsClientImpl] DNS 서버 응답 오류: status=%s",
                    response.status,
                )
                raise DnsServerException(
                    f"DNS 서버 응답 오류: {response.status}"
                )
        finally:
            response.release()
