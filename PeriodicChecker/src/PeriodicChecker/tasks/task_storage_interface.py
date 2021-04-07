from typing import List, Dict
from abc import abstractmethod, ABC
from PeriodicChecker.tasks.tasks import TaskInterface


class TaskStorageInterface(ABC):
    @abstractmethod
    async def init_storage(self, *args, **kwargs): ...

    @abstractmethod
    async def save(self, task: TaskInterface): ...

    def save_batch(self, tasks: List[TaskInterface]): ...

    @abstractmethod
    async def load(self, task_id: str) -> TaskInterface: ...

    @abstractmethod
    async def load_all(self) -> Dict[str, TaskInterface]: ...

    @abstractmethod
    async def close(self): ...
