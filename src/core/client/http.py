from abc import ABC, abstractmethod


class HttpClient(ABC):

    @abstractmethod
    async def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def post(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def put(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def patch(self, *args, **kwargs):
        raise NotImplementedError