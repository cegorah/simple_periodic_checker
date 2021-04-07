#!/bin/bash
set -a
source .env.prod
set +a
pip3 install -e .[tests]
gunicorn PeriodicChecker.producer_server:init_app --bind 0.0.0.0:8080 --worker-class aiohttp.GunicornWebWorker --reload --workers 16