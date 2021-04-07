import logging
from aiokafka.helpers import create_ssl_context
from asyncio import get_running_loop, all_tasks, current_task, gather
from PeriodicChecker.errors import *
from PeriodicChecker.tasks.sqlite_storage import SqliteKeeper
from PeriodicChecker.settings import TASK_DISPATCHER_SETTINGS, KAFKA_SETTINGS
from PeriodicChecker.broker.kafka_client import KafkaProducer
from PeriodicChecker.task_runner.runner import Runner
from PeriodicChecker.tasks.task_factory import TaskDispatcher

logger = logging.getLogger(__name__)


def kafka_ssl_context():
    try:
        context = create_ssl_context(
            cafile=KAFKA_SETTINGS.get("cafile"),
            certfile=KAFKA_SETTINGS.get("certfile"),
            keyfile=KAFKA_SETTINGS.get("keyfile"),
            password=KAFKA_SETTINGS.get("cert_password")
        )
    except Exception:
        context = None
    return context


async def service_init(app):
    loop = get_running_loop()
    sqlite_storage = SqliteKeeper(TASK_DISPATCHER_SETTINGS.get("storage_path"))
    await sqlite_storage.init_storage()
    task_dispatcher = TaskDispatcher(sqlite_storage)
    broker = KafkaProducer(connection_string=KAFKA_SETTINGS.get("connection_string"), ssl_context=kafka_ssl_context())
    task_runner = Runner(task_factory=task_dispatcher, broker=broker)
    await task_runner.init_runner()
    await broker.init_broker()
    app["task_dispatcher"] = task_dispatcher
    app["task_runner"] = task_runner
    loop.create_task(task_runner.main_loop())
    loop.set_exception_handler(general_error_handler)


def general_error_handler(loop, context):
    exception = context.get("exception")
    if isinstance(exception, BrokerErrors):
        logger.error(f"Could not send the message to the broker with the error {exception}")
        return
    if isinstance(exception, TaskError):
        fut = context.get("future").get_name()
        logger.error(f"Task {fut} error: {exception}")
        return
    logger.error(f"Somethings wrongs :{exception}")


async def cleanup(app):
    tasks = [t for t in all_tasks() if t is not current_task()]
    [task.cancel() for task in tasks]
    await gather(*tasks, return_exceptions=True)
    await app.get("task_runner").close()


startup_callbacks = {service_init}
cleanup_callbacks = {cleanup}
