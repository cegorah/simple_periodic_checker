import pickle
import aiosqlite
from typing import Dict
from sqlite3 import Binary

from PeriodicChecker.tasks.task_storage_interface import TaskStorageInterface, TaskInterface


class SqliteKeeper(TaskStorageInterface):
    def __init__(self, storage_path: str):
        self.storage_path = storage_path

    async def init_storage(self, *args, **kwargs):
        async with aiosqlite.connect(self.storage_path) as con:
            await con.execute("""CREATE TABLE IF NOT EXISTS tasks(ID VARCHAR(32) PRIMARY KEY, 
                                     NAME VARCHAR(32), URL VARCHAR(255), 
                                     COMMAND VARCHAR(255), OBJECT BLOB)""")
            await con.commit()

    async def save(self, task: TaskInterface):
        async with aiosqlite.connect(self.storage_path) as con:
            await con.execute("INSERT INTO tasks(ID, NAME, URL, COMMAND, OBJECT) VALUES (?, ?, ?, ?, ?)",
                              [str(task.task_id), task.name, task.url, task.command_type,
                               Binary(pickle.dumps(task))])
            await con.commit()

    async def load(self, task_id: str) -> TaskInterface:
        # TODO complete me
        pass
        # async with aiosqlite.connect(self.storage_path) as con:
        # async with con.execute("""SELECT ID, OBJECT FROM tasks WHERE ID = ?""", task_id) as cursor:

    async def load_all(self) -> Dict[str, TaskInterface]:
        tasks = dict()
        async with aiosqlite.connect(self.storage_path) as con:
            async with con.execute("""SELECT ID, OBJECT FROM tasks""") as cursor:
                async for r in cursor:
                    tasks[str(r[0])] = pickle.loads(r[1])
        return tasks

    async def close(self):
        ...
