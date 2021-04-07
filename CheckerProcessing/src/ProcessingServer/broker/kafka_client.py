import json
import asyncio
import logging

from aiokafka import AIOKafkaConsumer
from ProcessingServer.errors import *
from ProcessingServer.broker.broker_interface import BrokerInterface


class KafkaClient(BrokerInterface):
    def __init__(self):
        raise NotImplementedError("Use init_connection() instead")

    @classmethod
    async def init_connection(cls, connection_string: str = None, *topics, **kwargs):
        self = cls.__new__(cls)
        group_id = kwargs.get("group_id")
        ssl_context = kwargs.get("ssl_context")
        self.consumer = AIOKafkaConsumer(
            *topics,
            group_id=group_id,
            ssl_context=ssl_context,
            loop=asyncio.get_running_loop(), bootstrap_servers=connection_string
        )
        self.results = asyncio.Queue()
        return self

    async def read(self, **kwargs):
        await self.consumer.start()
        try:
            async for msg in self.consumer:
                logging.getLogger(__name__).info(f"Received message: {msg}")
                await self.results.put(json.loads(msg.value))
        except Exception as e:
            raise ReadMessageError(e)
        finally:
            await self.consumer.stop()

    async def close(self):
        await self.consumer.stop()

    async def send(self, message: str, channel_name: str, timeout: int = None, **kwargs):
        raise NotImplementedError("Just a consumer")
