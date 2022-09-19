# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

import inspect
from enum import Enum


class LoggerType(Enum):
    """This enum specifies logger type."""
    None_ = 'none'
    """No debug log."""

    HomeAppLogger = 'home_app_logger'
    """Logger for home app."""

    SettingAppLogger = 'setting_app_logger'
    """Logger for setting app."""

    BackgroundAppLogger = 'background_app_logger'
    """Logger for background app."""


class Logger:
    """This class outputs a debug log."""

    _logger_obj = None

    @classmethod
    def set_logger_type(cls, type=LoggerType.None_):
        """Sets logger type.
        If ``LoggerType.None_`` is given, no debug log is recorded.

        Args:
           type (LoggerType): Logger type.
        """
        if type is LoggerType.HomeAppLogger:
            from hmserver.apps.common.logger import logger_obj
            obj = logger_obj
        elif type is LoggerType.SettingAppLogger:
            from stserver.apps.common.logger import logger_obj
            obj = logger_obj
        elif type is LoggerType.BackgroundAppLogger:
            from webapplogger import logger_obj
            obj = logger_obj
        else:
            obj = None

        cls._logger_obj = obj

    @classmethod
    def _log(cls, frame, level='debug', message='', tag=None):
        if cls._logger_obj is None:
            return

        if tag is None:
            # Tag format is [{Source File Name} {Invoked Function Name}]
            filename = frame.f_code.co_filename

            # Extract file name from path
            index = filename.rfind('/')
            if index != -1:
                filename = filename[index + 1:]

            func = frame.f_code.co_name
            tag = '{0} {1}'.format(filename, func)

        cls._logger_obj.log(message, log_level=level, name=tag)

    @classmethod
    def debug(cls, message, tag=None):
        """Outputs a debug level log.

        Args:
            message (str): Log message.
            tag (str): Log message tag.
                If ``None`` is given, source file name and function name are recorded.
        """
        frame = inspect.currentframe().f_back
        cls._log(frame, 'debug', message, tag)

    @classmethod
    def info(cls, message, tag=None):
        """Outputs an info level log.

        Args:
            message (str): Log message.
            tag (str): Log message tag.
                If ``None`` is given, source file name and function name are recorded.
        """
        frame = inspect.currentframe().f_back
        cls._log(frame, 'info', message, tag)

    @classmethod
    def warn(cls, message, tag=None):
        """Outputs a warning level log.

        Args:
            message (str): Log message.
            tag (str): Log message tag.
                If ``None`` is given, source file name and function name are recorded.
        """
        frame = inspect.currentframe().f_back
        cls._log(frame, 'warning', message, tag)

    @classmethod
    def error(cls, message, tag=None):
        """Outputs an error level log.

        Args:
            message (str): Log message.
            tag (str): Log message tag.
                If ``None`` is given, source file name and function name are recorded.
        """
        frame = inspect.currentframe().f_back
        cls._log(frame, 'error', message, tag)
