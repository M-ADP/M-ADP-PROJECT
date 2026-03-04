from dataclasses import dataclass, field

from src.common.id_generator import IdGenerator


@dataclass
class Port:
    id: int = field(default_factory=IdGenerator.generate_sonyflake_id)
    project_id: int = 0
    from_ip: str = ""
    from_port: int = 0
    port_number: int = 0
    protocol: str = ""

    def update(
        self,
        from_ip: str,
        from_port: int,
        port_number: int,
        protocol: str,
    ) -> None:
        self.from_ip = from_ip
        self.from_port = from_port
        self.port_number = port_number
        self.protocol = protocol
