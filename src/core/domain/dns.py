import enum
from dataclasses import dataclass, field
from typing import Optional

from src.common.id_generator import IdGenerator


class DNSState(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"
    DELETED = "DELETED"


@dataclass
class DNS:
    id: str = field(default_factory=IdGenerator.generate_sonyflake_id)
    project_id: str = ""
    dns_name: str = ""
    state: DNSState = DNSState.PENDING
    port_id: Optional[str] = None

    def update_state(self, state: DNSState) -> None:
        self.state = state

    def bind_port(self, port_id: str) -> None:
        self.port_id = port_id

    def unbind_port(self) -> None:
        self.port_id = None
