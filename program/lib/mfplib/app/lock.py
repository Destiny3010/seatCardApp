# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from ..webapi import WebApi
from ..debug import Logger


class HomeAppLock:
    """This class manages home app lock."""

    _LOCK_API_URL = '/app/homeapp/lock'

    def __init__(self, api_token):
        """Initializes a new instance.

        Args:
            api_token (str): API access token.
        """
        self._api = WebApi(api_token)
        self._lock_id = None

    @property
    def locked(self):
        """Gets whether home app session is locked or not."""
        return self._lock_id is not None

    def acquire(self):
        """Acquires lock to keep home app session."""
        if self._lock_id:
            return

        response = self._api.post(self._LOCK_API_URL)
        self._lock_id = response['lock_id']
        Logger.info('Home app session is locked (lock ID: {}).'.format(self._lock_id))

    def release(self):
        """Releases home app session lock."""
        if self._lock_id is None:
            return

        self._api.delete(self._LOCK_API_URL, {'lock_id': self._lock_id})
        Logger.info('Home app session is unlocked (lock ID: {}).'.format(self._lock_id))
        self._lock_id = None
