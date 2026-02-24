from sqlalchemy import BigInteger, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.domain.port import Port as PortEntity
from src.common.id_generator import IdGenerator
from src.core.db import BaseEntity


class Port(BaseEntity):
    __tablename__ = "port"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "from_port",
            name="uq_port_project_from_port",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        default=IdGenerator.generate_sonyflake_id,
    )
    project_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("project.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_ip: Mapped[str] = mapped_column(String(255), nullable=False)
    from_port: Mapped[int] = mapped_column(BigInteger, nullable=False)
    port_number: Mapped[int] = mapped_column(Integer, nullable=False)
    protocol: Mapped[str] = mapped_column(String(16), nullable=False)

    def to_entity(self) -> PortEntity:
        return PortEntity(
            id=self.id,
            project_id=self.project_id,
            from_ip=self.from_ip,
            from_port=self.from_port,
            port_number=self.port_number,
            protocol=self.protocol,
        )
