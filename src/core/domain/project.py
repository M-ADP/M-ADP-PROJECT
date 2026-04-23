from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from src.common.id_generator import IdGenerator


@dataclass
class Project:
    id: int = field(default_factory=IdGenerator.generate_sonyflake_id)
    user_id: int = 0
    name: str = ""
    max_cpu: float = 0.0
    max_memory: float = 0.0
    max_disk: float = 0.0

    def update_name(self, name: str) -> None:
        self.name = name


@dataclass
class ProjectMember:
    id: int = field(default_factory=IdGenerator.generate_sonyflake_id)
    project_id: int = 0
    user_id: int = 0
    role: Literal["OWNER", "MEMBER"] = "MEMBER"
    joined_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProjectInvitation:
    id: int = field(default_factory=IdGenerator.generate_sonyflake_id)
    project_id: int = 0
    inviter_user_id: int = 0
    invitee_user_id: int = 0
    invitee_email: str = ""
    token_hash: str = ""
    status: Literal["PENDING", "ACCEPTED", "REJECTED", "CANCELED", "EXPIRED"] = "PENDING"
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=datetime.now)
    responded_at: datetime | None = None
