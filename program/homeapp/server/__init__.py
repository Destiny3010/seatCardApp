# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from pyramid.config import Configurator

from mfplib.debug import Logger, LoggerType

from . import routes


def includeme(config):
    # Setup logger
    Logger.set_logger_type(LoggerType.HomeAppLogger)

    # Adds routes
    routes.configure(config)


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include(includeme, route_prefix='/')
    config.scan()

    return config.make_wsgi_app()
