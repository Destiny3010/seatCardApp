# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from datetime import datetime

from . import session
from .client import CommunicationClient


class Task:
    """This class is an abstract task which is executed on background app."""

    def __init__(self):
        self.__api_token = None
        self.__dispatched_at = None
        self.__locale = None

    @property
    def api_token(self):
        """Gets an API access token."""
        return self.__api_token

    @property
    def dispatched_at(self):
        """Gets unix time stamp at task dispatched."""
        return self.__dispatched_at

    @property
    def locale(self):
        """Gets locale in home app session."""
        return self.__locale

    def dispatch(self, api_token):
        """Dispatches task to background via existing communication connection.
        If connection is not opened yet, this method will open by itself.

        Args:
            api_token (str): API access token.
        Raises:
            CommunicationError: Background app is not started or does not open connection.
        """
        client = CommunicationClient.connect(api_token)
        client.request(
            handler_path='mfplib.app.background.handlers.task.TaskHandler',
            body={
                'dispatched_at': datetime.now().timestamp(),
                'locale': session.get_locale(api_token),
                'task': self,
            },
        )

    def execute(self, payload=None):
        """This is an abstract method to execute a task."""
        raise NotImplementedError('execute method is not implemented.')

    def _set_task_attributes(self, api_token, dispatched_at, locale):
        """Sets task attributes."""
        self.__api_token = api_token
        self.__dispatched_at = dispatched_at
        self.__locale = locale

    def on_enqueued(self, payload=None):
        """This method is invoked at task enqueued in background.

        Args:
            payload (TaskPayload): Dispatched task payload.
        """
        pass

    def on_aborted(self):
        """This method is invoked at task aborted."""
        pass

    def on_error(self, error):
        """This method is invoked at task failed while executing.

        Args:
            error (Exception): Error object.
        """
        pass
