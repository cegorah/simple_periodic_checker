import re
import uuid
import time
from typing import Generic, TypeVar
from datetime import datetime
from abc import ABC, abstractmethod
from aiohttp.client import ClientSession
from PeriodicChecker.errors import *

T = TypeVar("T")


class ResultQueue(Generic[T]):
    async def put(self, item): ...

    async def get(self): ...


class TaskInterface(ABC):
    __slots__ = "name", "url", "task_id", "regex", "command_type", "repeat", "retry", "sleep_time"

    @abstractmethod
    async def run(self, results: ResultQueue): ...


class FetchTask(TaskInterface):
    __slots__ = "name", "url", "task_id", "regex", "send_to", "command_type", "repeat", "retry", "sleep_time", "status"

    def __init__(self, *, name: str, url: str, command_type: str = "fetch", **params):
        self.url = url
        self.name = name
        self.status = "pending"
        self.task_id = str(uuid.uuid4())
        self.command_type = command_type

        self.send_to = params.get("send_to")

        regex = params.get("regex")
        self.regex = re.compile(regex.encode()) if regex else None

        self.retry = params.get("retry", 0)
        self.repeat = params.get("repeat", True)
        self.sleep_time = params.get("sleep_time", 0)

    async def run(self, results: ResultQueue):
        try:
            cur_time = datetime.now().strftime("%x - %X")
            start_time = time.time()
            async with ClientSession() as client:
                async with client.get(self.url) as resp:
                    body = await resp.read()
                    end_time = time.time()
                    res = {"name": self.name, "timestamp": cur_time, "status": resp.status,
                           "load_time": "{:.4f}".format(end_time - start_time)}
                    if self.regex:
                        res["pattern_search"] = "match" if re.search(self.regex, body) else None
            res = {self.task_id: res}
            await results.put(res)
        except Exception as e:
            raise TaskGeneralError(e)


class DeleteTask(TaskInterface):
    def __init__(self):
        raise NotImplementedError()

    async def run(self, results: ResultQueue):
        raise NotImplementedError()


class SendTask(TaskInterface):
    def __init__(self):
        raise NotImplementedError()

    async def run(self, results: ResultQueue):
        raise NotImplementedError()


tasks_dict = {"fetch": FetchTask}

__all__ = ["FetchTask", "tasks_dict"]
