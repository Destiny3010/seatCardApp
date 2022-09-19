# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from datetime import datetime

from . import session
from .client import CommunicationClient


class TaskPayload:
    """This class contains payload for background task."""

    def __init__(self, **kwargs):
        """Initializes a new instance."""
        for key, value in kwargs.items():
            setattr(self, key, value)


class Dispatcher:
    """This class dispatches tasks to background app."""

    def __init__(self, api_token):
        """Initializes a new instance.

        Args:
            api_token (str): API access token.
        """
        self._api_token = api_token

    def dispatch(self, task_class, payload):
        """Dispatches a payload of task to execute related task in background app.

        Args:
            task_class (str): Related task class path (e.g. tasks.upload.UploadTask).
                Task class must be implemented under 'lib' or 'backgroundapp' directory.
            payload (TaskPayload): Task payload.
                If payload class is inherited from TaskPayload class,
                the super class must be implemented under 'lib' directory.
        Raises:
            CommunicationError: Background app is not started or does not open connection.
        """
        client = CommunicationClient.connect(self._api_token)
        client.request(
            handler_path='mfplib.app.background.handlers.task_payload.TaskPayloadHandler',
            body={
                'task_class': task_class,
                'dispatched_at': datetime.now().timestamp(),
                'locale': session.get_locale(self._api_token),
                'payload': payload,
            },
        )
