#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys

from aiohttp import web
from schema import Schema, Or

import settings
from common.middlewares import error_middleware
from utils.utils import load_cfg

from service.handlers import handle_interpolate, handle_generate, handle_version


async def on_startup(app):
    config = app['CONFIG']
    app['months_data_lag'] = config['months_data_lag']
    app['months_mean_lag'] = config['months_mean_lag']


async def on_cleanup(app):
    pass


async def on_shutdown(app):
    pass


def add_routes(app):
    app.router.add_post('/interpolation', handle_interpolate)
    app.router.add_post('/generate', handle_generate)
    app.router.add_get('/version', handle_version)
    return app


def get_app(config: dict, val_request: bool = False):
    app = web.Application(middlewares=[error_middleware], debug=True)

    app['validate_request'] = val_request
    app['__version__'] = settings.__version__
    app['CONFIG'] = config
    if val_request:
        app['request_schema_interp'] = Schema({"data": [{"client_name": str,
                                                         "vin": str,
                                                         "model": str,
                                                         "date_service": str,
                                                         "max_interp_date": Or(None, str),
                                                         "odometer": Or(None, int),
                                                         "service_period": int}]})
        app['request_schema_generate'] = Schema({"client_name": str,
                                                 "vin": str,
                                                 "model": str,
                                                 "date_service": str,
                                                 "odometer": int,
                                                 "day_mean_km": int,
                                                 "exp_work_type": str,
                                                 "date_from": Or(None, str),
                                                 "service_period": int})

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.on_shutdown.append(on_shutdown)

    app.logger.info('Odometer service version: {}'.format(app['__version__']))
    return add_routes(app)


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            SERVICE_CONFIG = load_cfg(os.path.abspath(sys.argv[1]))
        else:
            SERVICE_CONFIG = load_cfg(os.path.join(settings.PROJECT_DIR, 'service', 'etc', 'config.yml'))

        logging.getLogger('asyncio').setLevel(logging.INFO)
        logging.basicConfig(level=logging.getLevelName(SERVICE_CONFIG['other']['log_level'].upper()),
                            format=settings.DEFAULT_LOG_FORMAT)

        web.run_app(get_app(SERVICE_CONFIG['other']),
                    host=SERVICE_CONFIG['service']['host'],
                    port=SERVICE_CONFIG['service']['port'])
    except FileNotFoundError as err:
        sys.exit(str(err))
