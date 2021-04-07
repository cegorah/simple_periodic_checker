import uuid
import asyncio
import logging
from random import randint
from typing import Dict
from abc import ABC, abstractmethod
from ProcessingServer.errors import *

logger = logging.getLogger(__name__)


class ProcessorInterface(ABC):
    __slots__ = "storage_name"

    def __init__(self): ...

    @abstractmethod
    async def process(self, params: Dict) -> Dict: ...

    @abstractmethod
    async def close(self): ...


class DefaultProcessor(ProcessorInterface):
    """
    Mock
    """
    def __init__(self):
        self.pid = uuid.uuid4()
        self.name = f"processor_{uuid.uuid4()}"

    async def process(self, params: dict):
        try:
            logger.info(f"Processed {params}")
            await asyncio.sleep(randint(0, 7))
            return {"processed": params}
        except Exception as e:
            logger.error(e)
            raise ProcessingError(f"{self.name} failed")

    async def close(self):
        pass
