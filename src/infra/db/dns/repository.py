from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.dns.model import DNS
from src.core.repository.dns_repository import DNSRepository
from src.infra.db.dns.model import DNS as DNSModel


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
        conditions = [DNSModel.dns_name == dns_name]
        if exclude_dns_id:
            conditions.append(DNSModel.id != exclude_dns_id)

        stmt = select(DNSModel.id).where(*conditions).limit(1)
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def exists_by_project(self, project_id: str) -> bool:
        """프로젝트에 DNS가 존재하는지 확인합니다."""
        stmt = (
            select(DNSModel.id)
            .where(DNSModel.project_id == project_id)
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def get_by_project(self, project_id: str) -> DNS | None:
        """프로젝트의 DNS를 조회합니다."""
        stmt = select(DNSModel).where(DNSModel.project_id == project_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return model.to_entity()

    async def get_by_id_for_project(
        self, dns_id: str, project_id: str
    ) -> DNS | None:
        """프로젝트의 DNS를 ID로 조회합니다."""
        stmt = select(DNSModel).where(
            DNSModel.id == dns_id,
            DNSModel.project_id == project_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return model.to_entity()

    async def insert(self, dns: DNS) -> DNS:
        """DNS를 삽입합니다."""
        model = DNSModel(
            id=dns.id,
            project_id=dns.project_id,
            dns_name=dns.dns_name,
            state=dns.state,
            port_id=dns.port_id,
        )
        self._session.add(model)
        await self._session.flush()
        return model.to_entity()

    async def delete(self, dns: DNS) -> None:
        """DNS를 삭제합니다."""
        model = await self._session.get(DNSModel, dns.id)
        if model is None:
            return
        await self._session.delete(model)
        await self._session.flush()

    async def update_name(
        self,
        dns_id: str,
        project_id: str,
        dns_name: str,
    ) -> DNS:
        """DNS 이름을 업데이트합니다."""
        stmt = select(DNSModel).where(
            DNSModel.id == dns_id,
            DNSModel.project_id == project_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError("DNS not found")
        model.dns_name = dns_name
        await self._session.flush()
        return model.to_entity()

    async def bind_port(
        self,
        dns_id: str,
        project_id: str,
        port_id: str,
    ) -> DNS:
        """DNS에 포트를 바인딩합니다."""
        stmt = select(DNSModel).where(
            DNSModel.id == dns_id,
            DNSModel.project_id == project_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError("DNS not found")
        model.port_id = port_id
        await self._session.flush()
        return model.to_entity()
