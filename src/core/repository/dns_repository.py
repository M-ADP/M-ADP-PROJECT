from abc import ABC, abstractmethod

from src.app.dns.model import DNS
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

    @abstractmethod
    async def insert(self, dns: DNS) -> DNS:
        """DNS를 삽입합니다."""
        pass

    @abstractmethod
    async def delete(self, dns: DNS) -> None:
        """DNS를 삭제합니다."""
        pass

    @abstractmethod
    async def update_name(
        self,
        dns_id: str,
        project_id: str,
        dns_name: str,
    ) -> DNS:
        """DNS 이름을 업데이트합니다."""
        pass

    @abstractmethod
    async def bind_port(
        self,
        dns_id: str,
        project_id: str,
        port_id: str,
    ) -> DNS:
        """DNS에 포트를 바인딩합니다."""
        pass
