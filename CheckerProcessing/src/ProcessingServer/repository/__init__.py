from typing import Any, Union, Dict
from abc import ABC, abstractmethod


class RepositoryInterface(ABC):
    @abstractmethod
    async def init_pool(self, dsn: Union[Dict, str]) -> Any: ...

    @abstractmethod
    async def raw_query(self, statement: str, params: Dict) -> Any: ...
