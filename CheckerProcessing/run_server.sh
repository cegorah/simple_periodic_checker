#!/bin/bash
set -a
source .env.prod
set +a
pip3 install -e .[tests]
chmod 754 ./src/ProcessingServer/consumer_server.py
./src/ProcessingServer/consumer_server.py