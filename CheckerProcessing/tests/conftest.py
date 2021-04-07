import pytest
import logging
from ProcessingServer.processing.processor import DefaultProcessor
from ProcessingServer.runner.task_runner import TaskRunner
from ProcessingServer.broker.kafka_client import KafkaClient
from ProcessingServer.repository.postgres_storage import PostgresClient
from ProcessingServer.settings import DATABASE_SETTINGS

log = logging.getLogger(__name__)


@pytest.fixture
def broker(loop):
    broker = loop.run_until_complete(KafkaClient.init_connection("localhost:9092", "test_topic", group_id="test_group"))
    yield broker
    loop.run_until_complete(broker.close())


@pytest.fixture
def database(loop):
    con_string = DATABASE_SETTINGS.get("connection")
    pool = loop.run_until_complete(PostgresClient.init_pool(con_string))
    yield pool
    loop.run_until_complete(pool.close())


@pytest.fixture
def main_runner(loop, database, broker):
    runner = loop.run_until_complete(
        TaskRunner.init_runner(broker=broker, database=database, processor=DefaultProcessor()))
    yield runner
    loop.run_until_complete(runner.close())
