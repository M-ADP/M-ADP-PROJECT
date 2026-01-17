from dataclasses import dataclass, field

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
