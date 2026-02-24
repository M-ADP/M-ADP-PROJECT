from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Double, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.domain.project import Project as ProjectEntity
from src.core.domain.project import ProjectMember as ProjectMemberEntity
from src.common.id_generator import IdGenerator
from src.core.db import BaseEntity


class Project(BaseEntity):
    __tablename__ = "project"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        default=IdGenerator.generate_sonyflake_id,
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


class ProjectMember(BaseEntity):
    __tablename__ = "project_member"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_member"),
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
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="MEMBER")
    joined_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    def to_entity(self) -> ProjectMemberEntity:
        role = "OWNER" if self.role == "OWNER" else "MEMBER"
        return ProjectMemberEntity(
            id=self.id,
            project_id=self.project_id,
            user_id=self.user_id,
            role=role,
            joined_at=self.joined_at,
        )
