from PeriodicChecker.broker.kafka_client import KafkaProducer


async def test_send_message(loop):
    pr = KafkaProducer(connection_string="localhost:9092")
    await pr.init_broker()
    await pr.send(message={"Some": "message"}, channel_name="fetch", timeout=None)
    await pr.close()
