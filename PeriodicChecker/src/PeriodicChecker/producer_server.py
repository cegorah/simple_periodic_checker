import os
import logging
import bjoern
from sys import argv
from aiohttp import web
from itertools import zip_longest
from typing import Dict, Callable
from aiomisc.log import basic_config
from setproctitle import setproctitle
from configargparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from PeriodicChecker import routes
from PeriodicChecker import connection_routine

logger = logging.getLogger(__name__)


def get_args():
    parser = ArgumentParser(
        auto_env_var_prefix="TMANAGER_",
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--api-address', default='0.0.0.0',
                        help='IPv4/IPv6 address API server would listen on')
    parser.add_argument('--api-port', default=8081,
                        help='TCP port API server would listen on')
    parser.add_argument('--log-level', default="DEBUG",
                        help='default logging level')
    args = parser.parse_args()
    return args


def init_app(sub_apps: Dict[str, web.Application] = None):
    """
    Main init routine.

    :param sub_apps: the dictionary contains prefix: sub_app that should be appended to the main app
    :return:
    """
    args = get_args()
    app = web.Application()
    app["args"] = args
    basic_config(level=log_level(args.log_level))
    if sub_apps:
        for prefix, sub_app in sub_apps.items():
            app.add_subapp(prefix, sub_app)
    app.add_routes([
        web.get("/status", routes.status),
        web.get("/tasks", routes.task_list),
        web.post("/add_task", routes.add_task),
    ])
    for st, cl in zip_longest(connection_routine.startup_callbacks, connection_routine.cleanup_callbacks):
        if st:
            app.on_startup.append(st)
        if cl:
            app.on_cleanup.append(cl)
    return app


def log_level(level):
    levels = {"debug": logging.DEBUG, "info": logging.INFO, "error": logging.ERROR, "warning": logging.WARNING}
    return levels.get(level.lower())


def main(sub_apps: Dict = None):
    setproctitle(os.path.basename(argv[0]))
    app = init_app(sub_apps)
    args = app.get("args")
    web.run_app(app, host=args.api_address, port=args.api_port)


if __name__ == "__main__":
    main()
