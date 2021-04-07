from abc import ABC, abstractmethod
from typing import List, Callable


class BrokerInterface(ABC):
    @abstractmethod
    async def init_connection(self, connection_string: str = None, *args, **kwargs) -> Callable: ...

    @abstractmethod
    async def send(self, message: str, channel_name: str, timeout: int = None, **kwargs): ...

    @abstractmethod
    async def read(self, channel_name: List[str], timeout: int, **kwargs): ...

    @abstractmethod
    async def close(self): ...
