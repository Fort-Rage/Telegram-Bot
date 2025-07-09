from abc import ABC, abstractmethod


class CRUD(ABC):
    @abstractmethod
    async def create(self, *args, **kwargs):
        pass

    @abstractmethod
    async def read(self, *args, **kwargs):
        pass

    @abstractmethod
    async def update(self, *args, **kwargs):
        pass

    @abstractmethod
    async def remove(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_obj(self, *args, **kwargs):
        pass
