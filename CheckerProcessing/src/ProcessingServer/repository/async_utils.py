import sqlalchemy as sa
from aiopg.sa import create_engine

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class AsyncPgWorker:
    """
    Some utils to provide common metadata operations.
    Inspired by:
    https://github.com/aio-libs/aiopg/issues/321#issuecomment-423349052
    """

    @classmethod
    async def init_pool(cls, dsn, load_data=True):
        self = cls.__new__(cls)
        self.dsn = dsn
        self.statement = None
        self.__table = None
        self.__metadata = sa.MetaData()
        self.connection_pool = await create_engine(dsn)
        self.mock_sa_engine = sa.create_engine(
            dsn, strategy="mock", executor=self._compile
        )
        if load_data:
            self.load_tables(metadata=self.__metadata)
        return self

    def load_tables(self, engine=None, metadata=None, only=None):
        """
        Could be useful for loading tables from database to the metadata within reflection.

        :param engine: the Sqlalchemy engine instance
        :param metadata: the metadata instance where the tables should be loaded
        :param only: the sequence of the tables that should be loaded
        :return: the metadata object with the tables reflection
        """
        if not engine:
            engine = sa.create_engine(self.dsn)
        if not metadata:
            metadata = self.__metadata
        metadata.reflect(bind=engine, only=only)
        return metadata

    async def create_tables(self, tables=None, execute=True):
        self.__metadata.create_all(self.mock_sa_engine, tables)
        if execute:
            async with self.connection_pool.acquire() as conn:
                await conn.execute(self.statement)

    async def drop_tables(self, tables=None, execute=False):
        self.metadata.drop_all(self.mock_sa_engine, tables)
        if execute:
            async with self.connection_pool.acquire() as conn:
                await conn.execute(self.statement)
            for t in tables:
                self.__metadata.remove(t)

    async def close(self):
        self.connection_pool.close()

    @property
    def table(self):
        return self.__table

    @table.setter
    def table(self, value):
        if isinstance(value, sa.Table):
            self.__table = value
        if isinstance(value, str):
            self.__table = self.__metadata.tables.get(value)

    @property
    def metadata(self):
        return self.__metadata

    @metadata.setter
    def metadata(self, value):
        self.__metadata = value

    def _compile(self, sql, *multiparams, **params):
        self.statement = str(sql.compile(dialect=self.mock_sa_engine.dialect))
        # print(self.statement)
