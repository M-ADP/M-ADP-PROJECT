from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class MetricPointData:
    timestamp: str
    value: float


@dataclass
class ResourceUsageData:
    cpu: list[MetricPointData] = field(default_factory=list)
    memory: list[MetricPointData] = field(default_factory=list)
    disk: list[MetricPointData] = field(default_factory=list)
    network: list[MetricPointData] = field(default_factory=list)
    traffic_per_hour: list[MetricPointData] = field(default_factory=list)


class ProjectResourceClient(ABC):
    @abstractmethod
    async def create(self): ...

    @abstractmethod
    async def delete(self): ...

    @abstractmethod
    async def open_port(self): ...

    @abstractmethod
    async def close_port(self): ...

    @abstractmethod
    async def update_port(self): ...

    @abstractmethod
    async def create_dns(self): ...

    @abstractmethod
    async def delete_dns(self): ...

    @abstractmethod
    async def update_dns(self): ...

    @abstractmethod
    async def mapping_dns_and_port(self): ...
    @abstractmethod
    async def allocate(self):
        """가용 자원 할당"""
        ...

    @abstractmethod
    async def get_usage(
        self,
        project_id: str,
        days: int = 7,
        interval_minutes: int = 60,
    ) -> ResourceUsageData:
        """최근 N일의 리소스 사용량 시계열을 조회합니다."""
        ...

    @abstractmethod
    async def verify_password(
        self,
        user_id: str,
        password: str,
    ) -> bool: ...
