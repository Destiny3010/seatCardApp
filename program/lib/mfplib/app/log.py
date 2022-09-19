# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from enum import Enum

from ..webapi import WebApi


class AppLogLevel(Enum):
    """This enum represents an app log level."""
    Info = 'info'
    Warning = 'warning'
    Error = 'error'


class AppLog:
    """This class writes an app log.

    Attributes:
        admin_only (bool): Output log for admin only or not.
    """

    _API_URL = '/mfpdevice/logs/application'

    def __init__(self, api_token, admin_only=False):
        """Initializes a new instance.

        Args:
            api_token (str): API access token.
            admin_only (bool): Output log for admin only or not.
        """
        self._api = WebApi(api_token)
        self.admin_only = admin_only

    def info(self, message):
        """Writes an info level app log.

        Args:
            message (str): App log message.
        """
        self.write(AppLogLevel.Info, message)

    def warn(self, message):
        """Writes a warning level app log.

        Args:
            message (str): App log message.
        """
        self.write(AppLogLevel.Warning, message)

    def error(self, message):
        """Writes an error level app log.

        Args:
            message (str): App log message.
        """
        self.write(AppLogLevel.Error, message)

    def write(self, level, message):
        """Writes an app log.

        Args:
            level (AppLogLevel): App log level.
            message (str): App log message.
        """
        self._api.post(self._API_URL, {
            'log_level': level.value,
            'message': message,
            'visibility': 'admin' if self.admin_only else 'user',
        })
