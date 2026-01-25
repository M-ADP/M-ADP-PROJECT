from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from src.common.id_generator import IdGenerator


@dataclass
class Project:
    id: str = field(default_factory=IdGenerator.generate_sonyflake_id)
    user_id: str = ""
    name: str = ""
    max_cpu: float = 0.0
    max_memory: float = 0.0
    max_disk: float = 0.0

    def update_name(self, name: str) -> None:
        self.name = name


@dataclass
class ProjectMember:
    id: str = field(default_factory=IdGenerator.generate_sonyflake_id)
    project_id: str = ""
    user_id: str = ""
    username: str = ""
    profile_image: str | None = None
    role: Literal["OWNER", "VIEWER"] = "VIEWER"
    joined_at: datetime = field(default_factory=datetime.now)
