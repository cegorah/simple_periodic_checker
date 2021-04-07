from typing import List
from abc import ABC, abstractmethod


class BrokerInterface(ABC):
    @abstractmethod
    async def init_broker(self): ...

    @abstractmethod
    async def send(self, message: str, channel_name: str, timeout: int = None, **kwargs): ...

    @abstractmethod
    async def read(self, channel_name: List[str], timeout: int, **kwargs): ...

    @abstractmethod
    async def close(self): ...
