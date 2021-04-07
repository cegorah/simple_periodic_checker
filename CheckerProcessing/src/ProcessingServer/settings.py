import os

KAFKA_SETTINGS = {
    "connection": os.getenv("KAFKA_CONNECTION") or "localhost:9092",
    "cafile": os.getenv("KAFKA_CA_PATH") or "./ca-cert",
    "certfile": os.getenv("KAFKA_CERT_PATH") or "./cert-signed",
    "keyfile": os.getenv("KAFKA_KEY_FILE") or "./cert-key",
    "cert_password": os.getenv("KAFKA_CERT_PASS"),
    "consumer_group": os.getenv("KAFKA_CONSUMER_GROUP"),
    "topics": os.getenv("KAFKA_CONSUMER_TOPICS") or "fetch, update"
}
DATABASE_SETTINGS = {
    "connection": os.getenv("POSTGRESQL_CONNECTION")
}
