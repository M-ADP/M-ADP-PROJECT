from dataclasses import dataclass, field

from src.common.id_generator import IdGenerator


@dataclass
class Port:
    id: int = field(default_factory=IdGenerator.generate_sonyflake_id)
    project_id: int = 0
    service_id: str = ""
    service_name: str = ""
    target_deployment_name: str = ""
    port: int = 0
    target_port: int = 0
    protocol: str = "TCP"
    service_type: str = "ClusterIP"

    def update(
        self,
        service_id: str,
        service_name: str,
        target_deployment_name: str,
        port: int,
        target_port: int,
        protocol: str,
        service_type: str,
    ) -> None:
        self.service_id = service_id
        self.service_name = service_name
        self.target_deployment_name = target_deployment_name
        self.port = port
        self.target_port = target_port
        self.protocol = protocol
        self.service_type = service_type