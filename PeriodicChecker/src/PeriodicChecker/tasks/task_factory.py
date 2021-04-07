from typing import Dict
from PeriodicChecker.tasks.tasks import tasks_dict, TaskInterface
from PeriodicChecker.tasks.task_storage_interface import TaskStorageInterface


class TaskDispatcher:
    def __init__(self, storage: TaskStorageInterface):
        self.storage = storage

    async def create_task(self, *, name: str, url: str, register: bool, command_type: str = "fetch",
                          **call_params) -> TaskInterface:
        task_obj = tasks_dict.get(command_type)
        if not task_obj:
            raise ValueError(f"Command type should be one of: {tasks_dict.keys()}")
        task = task_obj(name=name, url=url, command_type=command_type, **call_params)
        if register:
            await self.storage.save(task)
        return task

    async def load_tasks(self) -> Dict[str, TaskInterface]:
        return await self.storage.load_all()
