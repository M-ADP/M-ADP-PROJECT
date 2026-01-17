from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.port.models import Port
from src.core.repository.port_repository import PortRepository


class PortRepositoryImpl(PortRepository):
    """포트 Repository 구현체"""

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def exists_by_from_port(
        self,
        project_id: str,
        from_port: int,
        exclude_port_id: str | None = None,
    ) -> bool:
        """포트 중복 여부를 확인합니다."""
        conditions = [Port.project_id == project_id, Port.from_port == from_port]
        if exclude_port_id:
            conditions.append(Port.id != exclude_port_id)

        stmt = select(Port.id).where(*conditions).limit(1)
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def insert(self, port: Port) -> Port:
        """포트를 삽입합니다."""
        self._session.add(port)
        await self._session.flush()
        return port

    async def list_by_project(
        self,
        project_id: str,
        limit: int,
        cursor: str | None = None,
    ) -> list[Port]:
        """프로젝트의 포트 목록을 조회합니다."""
        conditions = [Port.project_id == project_id]
        if cursor:
            conditions.append(Port.id > cursor)

        stmt = (
            select(Port)
            .where(*conditions)
            .order_by(Port.id)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_for_project(
        self,
        project_id: str,
        port_id: str,
    ) -> Port | None:
        """프로젝트의 포트를 ID로 조회합니다."""
        stmt = select(Port).where(Port.id == port_id, Port.project_id == project_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, port: Port) -> None:
        """포트를 삭제합니다."""
        await self._session.delete(port)
        await self._session.flush()
