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
            "service_id",
            name="uq_port_project_service_id",
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
    service_id: Mapped[str] = mapped_column(String(255), nullable=False)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_deployment_name: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    target_port: Mapped[int] = mapped_column(Integer, nullable=False)
    protocol: Mapped[str] = mapped_column(String(16), nullable=False, default="TCP")
    service_type: Mapped[str] = mapped_column(String(32), nullable=False, default="ClusterIP")

    def to_entity(self) -> PortEntity:
        return PortEntity(
            id=self.id,
            project_id=self.project_id,
            service_id=self.service_id,
            service_name=self.service_name,
            target_deployment_name=self.target_deployment_name,
            port=self.port,
            target_port=self.target_port,
            protocol=self.protocol,
            service_type=self.service_type,
        )