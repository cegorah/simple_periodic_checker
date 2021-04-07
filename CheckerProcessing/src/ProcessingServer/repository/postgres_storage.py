import logging
from psycopg2 import ProgrammingError
from warnings import warn
from aiopg import create_pool
from psycopg2.sql import SQL
from ProcessingServer.repository import RepositoryInterface

log = logging.getLogger(__name__)


class PostgresClient(RepositoryInterface):
    def __init__(self):
        raise NotImplementedError("Use init_pool() instead")

    async def __create_tables(self):
        await self.raw_query(
            """CREATE TABLE IF NOT EXISTS Tasks(
                "id" SERIAL PRIMARY KEY,
                "task_id" uuid UNIQUE, 
                "task_name" VARCHAR(64),
                "command" VARCHAR(64)
            )"""
        )
        await self.raw_query(
            """CREATE TABLE IF NOT EXISTS Process(
                "id" serial PRIMARY KEY,
                "process_id" uuid UNIQUE,
                "process_name" VARCHAR(64)
            )"""
        )
        await self.raw_query(
            """CREATE TABLE IF NOT EXISTS ProcessedResult (
                "process_id" uuid,
                "task_id" uuid,
                "result" VARCHAR(255),
                FOREIGN KEY (process_id) REFERENCES Process (process_id) ON DELETE CASCADE ,
                FOREIGN KEY (task_id) REFERENCES Tasks (task_id) ON DELETE NO ACTION 
            )"""
        )
        await self.raw_query(
            """CREATE TABLE IF NOT EXISTS RawResult(
                "task_id" uuid, 
                "result" VARCHAR(255),
                FOREIGN KEY (task_id) REFERENCES Tasks (task_id) ON DELETE NO ACTION 
            )"""
        )

    @classmethod
    async def init_pool(cls, dsn):
        self = cls.__new__(cls)
        self.dsn = dsn
        self.connection_pool = await create_pool(dsn)
        await self.__create_tables()
        return self

    async def raw_query(self, statement: str, params: dict = None, table_name: str = None):
        try:
            result = list()
            if table_name:
                warn("SECURITY: table_name will not be quoted", SyntaxWarning)
                statement = SQL(statement.format(table_name))
            async with self.connection_pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(statement, params)
                    if cursor.rowcount > 0:
                        res = await cursor.fetchmany(cursor.rowcount)
                        for r in res:
                            result.append(r)
            log.debug(f"Statement execute: {statement} with params {params}")
            return result
        except ProgrammingError as e:
            log.debug(e)
            pass
        except Exception as e:
            log.error(e)

    async def close(self):
        self.connection_pool.close()
