from abc import ABC, abstractmethod

from src.app.dns.models import DNS
from src.core.repository.base import Repository


class DNSRepository(Repository[DNS], ABC):
    """DNS Repository 추상 클래스"""

    @abstractmethod
    async def exists_by_dns_name(
        self,
        dns_name: str,
        exclude_dns_id: str | None = None,
    ) -> bool:
        """DNS 이름 중복 여부를 확인합니다."""
        pass

    @abstractmethod
    async def exists_by_project(self, project_id: str) -> bool:
        """프로젝트에 DNS가 존재하는지 확인합니다."""
        pass

    @abstractmethod
    async def get_by_project(self, project_id: str) -> DNS | None:
        """프로젝트의 DNS를 조회합니다."""
        pass

    @abstractmethod
    async def get_by_id_for_project(
        self, dns_id: str, project_id: str
    ) -> DNS | None:
        """프로젝트의 DNS를 ID로 조회합니다."""
        pass
