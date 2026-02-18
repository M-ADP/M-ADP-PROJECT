from typing import Optional

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.domain.dns import DNS as DNSEntity
from src.core.domain.dns import DNSState
from src.common.id_generator import IdGenerator
from src.core.db import BaseEntity


class DNS(BaseEntity):
    __tablename__ = "dns"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=IdGenerator.generate_sonyflake_id,
    )
    project_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("project.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    dns_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    state: Mapped[DNSState] = mapped_column(
        Enum(DNSState),
        nullable=False,
        default=DNSState.PENDING,
    )

    # Port binding - reference to existing Port
    port_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("port.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    def to_entity(self) -> DNSEntity:
        return DNSEntity(
            id=self.id,
            project_id=self.project_id,
            dns_name=self.dns_name,
            state=self.state,
            port_id=self.port_id,
        )
