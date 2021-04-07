import asyncio
import logging
from PeriodicChecker.tasks.tasks import TaskInterface
from PeriodicChecker.errors import *
from PeriodicChecker.broker.broker_interface import BrokerInterface

log = logging.getLogger(__name__)


class Runner:
    def __init__(self, *, task_factory, broker: BrokerInterface, load_stored: bool = True):
        self.failed = set()
        self.completed = set()
        self.broker = broker
        self.task_factory = task_factory
        self.load_stored = load_stored

    async def init_runner(self):
        self.loop = asyncio.get_running_loop()
        self.results = asyncio.queues.Queue()
        self.tasks = await self.task_factory.load_tasks() if self.load_stored else dict()
        loop = self.loop
        for task in self.tasks.values():
            job = loop.create_task(self.run_task(task))
            job.set_name(task.task_id)

    async def main_loop(self):
        assert hasattr(self, "results"), "Use init_runner() to initialize the runner"
        loop = self.loop
        while True:
            res = await self.results.get()
            task_id = next(iter(res))
            task = self.tasks.get(task_id)
            exception = res.get(task_id).get("exception")
            if task:
                if exception:
                    """Trying to retry the task if exception is acquired"""
                    if task.retry:
                        job = loop.create_task(self.run_task(task))
                        job.set_name(task_id)
                        log.error(f"Retry the task {task_id} with error {exception}")
                    else:
                        """The task completely failed and discarded"""
                        self.tasks.pop(task_id)
                        self.failed.add(task)
                        log.error(f"The task {task_id} completely failed")
                    task.retry -= 1
                    continue
                if task.repeat < 0:
                    """Repeat the task until the counter"""
                    self.tasks.pop(task_id)
                    continue
                job = loop.create_task(self.run_task(task))
                job.set_name(task.task_id)
                log.info(f"Repeat the task {task_id}")
                if task.send_to:
                    await self.broker.send(message=res, channel_name=task.send_to, key=task_id.encode())

    async def run_task(self, task: TaskInterface):
        try:
            if task.task_id not in self.tasks:
                self.tasks[task.task_id] = task
                await task.run(self.results)
                return
            sleep_time = task.sleep_time
            await asyncio.sleep(sleep_time)
            await task.run(self.results)
            if not isinstance(task.repeat, bool):
                task.repeat -= 1
        except TaskGeneralError as e:
            """Return the exception to the main_loop and raize for main error handler"""
            await self.results.put({task.task_id: {"exception": e}})
            raise e

    async def close(self):
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        if self.broker:
            await self.broker.close()
