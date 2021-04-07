import json
from typing import List, Dict

from aiokafka import AIOKafkaProducer
from asyncio import wait_for

from PeriodicChecker.errors import *
from PeriodicChecker.broker.broker_interface import BrokerInterface


class KafkaProducer(BrokerInterface):

    def __init__(self, connection_string: str, **kwargs):
        self.producer = AIOKafkaProducer(bootstrap_servers=connection_string,
                                         **kwargs)
        self.started = False

    async def init_broker(self):
        await self.producer.start()
        self.started = True

    async def send(self, *, message: Dict, channel_name: str, timeout: int = 2, **kwargs):
        assert self.started, "Call init_broker() for proper initialization"
        # TODO message validation?
        try:
            message = json.dumps(message)
            if timeout:
                await wait_for(self.producer.send(topic=channel_name.lower(), value=message.encode(), **kwargs),
                               timeout)
            else:
                await self.producer.send_and_wait(topic=channel_name.lower(), value=message.encode(), **kwargs)
        except Exception as e:
            raise SendMessageError(e)

    async def read(self, channel_name: List[str], timeout: int, **kwargs):
        raise NotImplementedError("Just a producer")

    async def close(self):
        await self.producer.stop()


__all__ = ["KafkaProducer"]
