from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.dns.models import DNS
from src.core.repository.dns_repository import DNSRepository


class DNSRepositoryImpl(DNSRepository):
    """DNS Repository 구현체"""

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def exists_by_dns_name(
        self,
        dns_name: str,
        exclude_dns_id: str | None = None,
    ) -> bool:
        """DNS 이름 중복 여부를 확인합니다."""
        conditions = [DNS.dns_name == dns_name]
        if exclude_dns_id:
            conditions.append(DNS.id != exclude_dns_id)

        stmt = select(DNS.id).where(*conditions).limit(1)
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def exists_by_project(self, project_id: str) -> bool:
        """프로젝트에 DNS가 존재하는지 확인합니다."""
        stmt = select(DNS.id).where(DNS.project_id == project_id).limit(1)
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def get_by_project(self, project_id: str) -> DNS | None:
        """프로젝트의 DNS를 조회합니다."""
        stmt = select(DNS).where(DNS.project_id == project_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_for_project(
        self, dns_id: str, project_id: str
    ) -> DNS | None:
        """프로젝트의 DNS를 ID로 조회합니다."""
        stmt = select(DNS).where(DNS.id == dns_id, DNS.project_id == project_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def insert(self, dns: DNS) -> DNS:
        """DNS를 삽입합니다."""
        self._session.add(dns)
        await self._session.flush()
        return dns

    async def delete(self, dns: DNS) -> None:
        """DNS를 삭제합니다."""
        await self._session.delete(dns)
        await self._session.flush()
