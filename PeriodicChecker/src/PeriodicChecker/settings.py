import os

KAFKA_SETTINGS = {
    "connection_string": os.getenv("TMANAGER_BROKER_CONNECTION") or "localhost:9092",
    "cafile": os.getenv("TMANAGER_KAFKA_CA_PATH") or "./ca-cert",
    "certfile": os.getenv("TMAMANGER_KAFKA_CERT_PATH") or "./cert-signed",
    "keyfile": os.getenv("TMANAGER_KAFKA_KEY_FILE") or "./cert-key",
    "cert_password": os.getenv("TMANAGER_KAFKA_CERT_PASS")
}

TASK_DISPATCHER_SETTINGS = {
    "storage_path": os.getenv("TMANAGER_TASK_STORAGE") or "./task_storage.db"
}
