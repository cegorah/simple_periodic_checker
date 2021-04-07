#!/usr/bin/env python3
import os
import asyncio
import logging
from aiokafka.helpers import create_ssl_context
from ProcessingServer.settings import KAFKA_SETTINGS, DATABASE_SETTINGS
from ProcessingServer.runner.task_runner import TaskRunner
from ProcessingServer.broker.kafka_client import KafkaClient
from ProcessingServer.processing.processor import DefaultProcessor
from ProcessingServer.repository.postgres_storage import PostgresClient


def log_level():
    levels = {"debug": logging.DEBUG, "info": logging.INFO, "error": logging.ERROR, "warning": logging.WARNING}
    env_param = os.getenv("LOG_LEVEL", "ERROR").lower()
    return levels.get(env_param)


def kafka_ssl_context():
    try:
        context = create_ssl_context(
            cafile=KAFKA_SETTINGS.get("cafile"),
            certfile=KAFKA_SETTINGS.get("certfile"),
            keyfile=KAFKA_SETTINGS.get("keyfile"),
            password=KAFKA_SETTINGS.get("cert_password")
        )
    except FileNotFoundError:
        context = None
    return context


async def init_services():
    topics = [k.strip() for k in KAFKA_SETTINGS.get("topics").split(",")]
    broker = await KafkaClient.init_connection(KAFKA_SETTINGS.get("connection"),
                                               *topics,
                                               ssl_context=kafka_ssl_context(),
                                               group_id=KAFKA_SETTINGS.get("consumer_group"))
    database = await PostgresClient.init_pool(DATABASE_SETTINGS.get("connection"))
    runner = await TaskRunner.init_runner(broker=broker, database=database, processor=DefaultProcessor())
    return runner


async def main():
    try:
        runner = await init_services()
        await runner.main_loop()
    finally:
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        await runner.close()


if __name__ == "__main__":
    try:
        logging.basicConfig(level=log_level())
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
