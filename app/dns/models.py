import enum
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from core.db import BaseEntity


class DNSState(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"
    DELETED = "DELETED"


class DNS(BaseEntity):
    __tablename__ = "dns"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("project.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    dns_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
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

    def update_state(self, state: DNSState):
        self.state = state

    def bind_port(self, port_id: str):
        self.port_id = port_id

    def unbind_port(self):
        self.port_id = None
