from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.port.model import Port
from src.core.repository.port_repository import PortRepository
from src.infra.db.port.model import Port as PortModel


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
        conditions = [
            PortModel.project_id == project_id,
            PortModel.from_port == from_port,
        ]
        if exclude_port_id:
            conditions.append(PortModel.id != exclude_port_id)

        stmt = select(PortModel.id).where(*conditions).limit(1)
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def insert(self, port: Port) -> Port:
        """포트를 삽입합니다."""
        model = PortModel(
            id=port.id,
            project_id=port.project_id,
            from_ip=port.from_ip,
            from_port=port.from_port,
            port_number=port.port_number,
            protocol=port.protocol,
        )
        self._session.add(model)
        await self._session.flush()
        return model.to_entity()

    async def list_by_project(
        self,
        project_id: str,
        limit: int,
        cursor: str | None = None,
    ) -> list[Port]:
        """프로젝트의 포트 목록을 조회합니다."""
        conditions = [PortModel.project_id == project_id]
        if cursor:
            conditions.append(PortModel.id > cursor)

        stmt = (
            select(PortModel)
            .where(*conditions)
            .order_by(PortModel.id)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [model.to_entity() for model in models]

    async def get_by_id_for_project(
        self,
        project_id: str,
        port_id: str,
    ) -> Port | None:
        """프로젝트의 포트를 ID로 조회합니다."""
        stmt = select(PortModel).where(
            PortModel.id == port_id,
            PortModel.project_id == project_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return model.to_entity()

    async def delete(self, port: Port) -> None:
        """포트를 삭제합니다."""
        model = await self._session.get(PortModel, port.id)
        if model is None:
            return
        await self._session.delete(model)
        await self._session.flush()

    async def update(
        self,
        project_id: str,
        port_id: str,
        from_ip: str,
        from_port: int,
        port_number: int,
        protocol: str,
    ) -> Port:
        """포트를 업데이트합니다."""
        stmt = select(PortModel).where(
            PortModel.id == port_id,
            PortModel.project_id == project_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError("Port not found")
        model.from_ip = from_ip
        model.from_port = from_port
        model.port_number = port_number
        model.protocol = protocol
        await self._session.flush()
        return model.to_entity()
