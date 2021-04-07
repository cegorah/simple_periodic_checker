import asyncio
import json
import logging
from ProcessingServer.errors import *
from ProcessingServer.processing.processor import ProcessorInterface
from ProcessingServer.broker.broker_interface import BrokerInterface
from ProcessingServer.repository.postgres_storage import RepositoryInterface

log = logging.getLogger(__name__)


class TaskRunner:
    @classmethod
    async def init_runner(cls, *, broker: BrokerInterface, database: RepositoryInterface,
                          processor: ProcessorInterface = None):
        """
        The main TaskRunner that will be dispatched the messages from the broker based on fields in the message.
        If the pattern_match == match pass the message
        to the Processor and store the result to the processedresult table.
        Otherwise store the message to the rawresult table.

        :param broker:
        :param database:
        :param processor:
        :return:
        """
        self = cls.__new__(cls)
        self.broker = broker
        self.database = database
        self.processor = processor
        return self

    async def main_loop(self):
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(self.exception_handler)
        loop.create_task(self.broker.read())
        # TODO Exception handler
        while True:
            broker_result = await self.broker.results.get()
            task_key = next(iter(broker_result))
            values = broker_result.get(task_key)
            await self.database.raw_query(
                "INSERT INTO tasks (TASK_ID, TASK_NAME, COMMAND) VALUES (%s, %s, %s) ON "
                "CONFLICT (TASK_ID) DO NOTHING ",
                params=[task_key, values.get("name"), values.get("command")]
            )
            if values.get("pattern_search") == "match" and self.processor:
                loop.create_task(self.process(task_key, values))
            else:
                await self.database.raw_query("INSERT INTO rawresult(task_id, result) VALUES (%s, %s)",
                                              params=[task_key, json.dumps(values)])

    def exception_handler(self, loop, context):
        exception = context.get("exception")
        if isinstance(exception, DatabaseError):
            log.error(f"Repository general error: {exception}")
        if isinstance(exception, ReadMessageError):
            log.error(f"Could not read the message: {exception}")
        if isinstance(exception, ProcessingError):
            log.error(f"Proccessor {exception} error")

    async def process(self, task_key, values):
        loop = asyncio.get_running_loop()
        process_task = loop.create_task(self.processor.process(values))
        await self.database.raw_query(
            "INSERT INTO process (process_id, process_name) VALUES (%s,%s) ON CONFLICT (process_id) DO NOTHING",
            params=[self.processor.pid, self.processor.name]
        )
        while not process_task.done():
            await asyncio.sleep(0)
        await self.database.raw_query(
            "INSERT INTO processedresult(process_id, task_id, result) VALUES (%s, %s, %s)",
            params=[self.processor.pid, task_key, json.dumps(process_task.result())]
        )

    async def close(self):
        await self.broker.close()
        await self.database.close()
        await self.processor.close()
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
