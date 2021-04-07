import os
import pytest
import logging
import asyncio

from PeriodicChecker.producer_server import init_app
from PeriodicChecker.task_runner.runner import Runner
from PeriodicChecker.broker.kafka_client import KafkaProducer
from PeriodicChecker.tasks.task_factory import TaskDispatcher
from PeriodicChecker.tasks.sqlite_storage import SqliteKeeper

log = logging.getLogger(__name__)
default_storage_path = "./tests/test_db.db"


@pytest.fixture(scope="session")
def session_loop(request):
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
def task_storage(session_loop):
    keeper = SqliteKeeper(default_storage_path)
    session_loop.run_until_complete(keeper.init_storage())
    return keeper


@pytest.fixture(scope="session")
def task_dispatcher(session_loop, task_storage):
    return TaskDispatcher(task_storage)


@pytest.fixture(scope="session")
def task_runner(session_loop, task_dispatcher):
    runner = Runner(task_factory=task_dispatcher, broker=None)
    session_loop.run_until_complete(runner.init_runner())
    yield runner
    session_loop.run_until_complete(runner.close())


@pytest.fixture(scope="session")
def broker(session_loop):
    producer = KafkaProducer(connection_string="localhost:9092", loop=session_loop)
    broker = session_loop.run_until_complete(producer.init_broker())
    yield broker
    session_loop.run_until_complete(broker.close())


@pytest.fixture
def api_cli(loop, aiohttp_client):
    app = loop.run_until_complete(init_app())
    return loop.run_until_complete(aiohttp_client(app))
