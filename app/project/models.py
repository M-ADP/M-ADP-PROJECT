from typing import Optional

from sqlalchemy import Double, String
from sqlalchemy.orm import Mapped, mapped_column

from core.db import BaseEntity


class Project(BaseEntity):
    __tablename__ = "project"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dns_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    max_cpu: Mapped[float] = mapped_column(Double, nullable=False)
    max_memory: Mapped[float] = mapped_column(Double, nullable=False)
    max_disk: Mapped[float] = mapped_column(Double, nullable=False)
