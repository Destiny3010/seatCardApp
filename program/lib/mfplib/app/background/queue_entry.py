# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from ...debug import Logger
from ...webapi import WebApi


class SessionLock:
    """This class lock home app session in background."""

    _LOCK_API_URL = '/app/communication/server/lock'

    def __init__(self, api_token, lock_id):
        """Initializes a new instance."""
        self._api_token = api_token
        self._lock_id = lock_id

    @property
    def locked(self):
        """Gets whether session is locked or not."""
        return bool(self._lock_id)

    @classmethod
    def acquire(cls, api_token):
        """Acquires a lock to keep job session.

        Args:
            api_token (str): API access token in home app session.
        """
        api = WebApi(api_token)
        response = api.post(cls._LOCK_API_URL)
        lock_id = response['lock_id']

        Logger.info('Task session is locked by ID "{}".'.format(lock_id))

        return cls(api_token, lock_id)

    def release(self):
        """Releases an existing lock."""
        if self._lock_id is None:
            return

        api = WebApi(self._api_token)
        api.delete(self._LOCK_API_URL, {'lock_id': self._lock_id})
        Logger.info('Task session lock (ID: {}) is released.'.format(self._lock_id))

        self._lock_id = None


class QueueEntry:
    """This class hosts a task."""

    def __init__(self, task, payload=None):
        """Initializes a new instance.

        Args:
            task (Task): Requested task.
            payload (TaskPayload): Task payload.
        """
        self._task = task
        self._payload = payload

        self._lock = None

    @property
    def task(self):
        """Gets a requested task."""
        return self._task

    @property
    def payload(self):
        """Gets a task payload."""
        return self._payload

    @property
    def locked(self):
        """Gets whether session is locked or not."""
        return bool(self._lock)

    def lock_session(self, api_token):
        """Acquires a lock to keep job session."""
        self._lock = SessionLock.acquire(api_token)

    def unlock_session(self):
        """Releases an existing lock."""
        if not self._lock:
            return  # session is not locked

        self._lock.release()
        self._lock = None
