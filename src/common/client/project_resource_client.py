from abc import ABC, abstractmethod


class ProjectResourceClient(ABC):

    @abstractmethod
    async def create(self):
        ...

    @abstractmethod
    async def delete(self):
        ...

    @abstractmethod
    async def open_port(self):
        ...

    @abstractmethod
    async def close_port(self):
        ...

    @abstractmethod
    async def update_port(self):
        ...

    @abstractmethod
    async def create_dns(self):
        ...

    @abstractmethod
    async def delete_dns(self):
        ...

    @abstractmethod
    async def update_dns(self):
        ...

    @abstractmethod
    async def mapping_dns_and_port(self):
        ...

    @abstractmethod
    async def allocate(self):
        """가용 자원 할당"""
        ...