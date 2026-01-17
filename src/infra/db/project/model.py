from sqlalchemy import Double, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.project.model import Project as ProjectEntity
from src.common.id_generator import IdGenerator
from src.core.db import BaseEntity


class Project(BaseEntity):
    __tablename__ = "project"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default_factory=IdGenerator.generate_sonyflake_id,
    )
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    max_cpu: Mapped[float] = mapped_column(Double, nullable=False)
    max_memory: Mapped[float] = mapped_column(Double, nullable=False)
    max_disk: Mapped[float] = mapped_column(Double, nullable=False)

    def to_entity(self) -> ProjectEntity:
        return ProjectEntity(
            id=self.id,
            user_id=self.user_id,
            name=self.name,
            max_cpu=self.max_cpu,
            max_memory=self.max_memory,
            max_disk=self.max_disk,
        )
