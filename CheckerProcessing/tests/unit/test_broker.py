import json
import pytest
from asyncio import queues, get_running_loop
from aiokafka.producer.producer import AIOKafkaProducer


async def test_send_ping(broker):
    mes = json.dumps({"Something": "good"})
    broker.results = queues.Queue()
    broker_producer = AIOKafkaProducer()
    await broker_producer.start()
    get_running_loop().create_task(broker.read())
    await broker_producer.send("test_topic", value=mes.encode())
    res = await broker.results.get()
    await broker_producer.stop()
    await broker.close()
    assert mes == json.dumps(res)


@pytest.mark.xfail
async def test_invalid_json(broker):
    mes = "somemessage"
    broker.results = queues.Queue()
    broker_producer = AIOKafkaProducer()
    await broker_producer.start()
    job = get_running_loop().create_task(broker.read())
    await broker_producer.send("test_topic", value=mes.encode())
    await broker_producer.stop()
    await broker.close()
    job.cancel()
