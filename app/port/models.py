from sqlalchemy import BigInteger, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.db import BaseEntity


class Port(BaseEntity):
    __tablename__ = "port"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "from_port",
            name="uq_port_project_from_port",
        ),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("project.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_ip: Mapped[str] = mapped_column(String(255), nullable=False)
    from_port: Mapped[int] = mapped_column(BigInteger, nullable=False)
    port_number: Mapped[int] = mapped_column(Integer, nullable=False)
    protocol: Mapped[str] = mapped_column(String(16), nullable=False)

    def update(self, from_ip, from_port, port_number, protocol):
        self.from_ip = from_ip
        self.from_port = from_port
        self.port_number = port_number
        self.protocol = protocol