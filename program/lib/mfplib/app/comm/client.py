# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

import itertools
import pickle
import base64
from threading import Lock

from ...webapi import WebApi, WebApiError
from ...debug import Logger


class CommunicationError(Exception):
    """This class represents an app communication error."""
    pass


class CommunicationClient:
    """This class manages app communication on client side."""

    _OPEN_API_URL = '/app/communication/client'
    _CONNECTION_API_URL = '/app/communication/client/{}'

    _RETRY_COUNT = 1

    _lock = Lock()
    _singleton = None

    def __init__(self, api_token, connection_id):
        self._api_token = api_token
        self._connection_id = connection_id

    @classmethod
    def connect(cls, api_token, refresh=False):
        """Connects to background app.
        If already connection has been established in app session,
        the existing connection is re-used (connection open step is skipped).

        Args:
            api_token (str): API access token.
            refresh (bool): If true is given, new connection will be established regardless an existing connection.
        Returns:
            CommunicationClient: Communication client.
        Raises:
            CommunicationError: Background app is not started or does not open connection.
        """
        if not cls._lock.acquire(timeout=10):
            raise RuntimeError('Cannot acquire communication connection.')

        try:
            # Use cached connection client if existing
            client = cls._singleton
            if not refresh and client and client._api_token == api_token:
                Logger.info('Existing connection is used for app communication.')
                return client

            # Open new connection
            connection_id = cls._establish_connection(api_token)
            client = cls(api_token, connection_id)
            Logger.warn('App communication is established using connection ID "{}".'.format(connection_id))

            CommunicationClient._singleton = client  # Cache established connection
            return client
        finally:
            cls._lock.release()

    def request(self, handler_path, body=None):
        """Sends a request to background app via established connection.

        Args:
            handler_path (str): Handler class path (e.g. package.SomeHandler).
            body (object): Request body.
        Returns:
            object: Response data.
        Raises:
            CommunicationError: Background app is not started or does not open connection.
        Note:
            Request body can include an object but the object must be serializable.
        """
        api = WebApi(self._api_token)

        # Build message object
        request = {
            'handler_path': handler_path,
            'body': {} if body is None else body,
        }

        # Serializes message
        dump = pickle.dumps(request)
        serialized = base64.b64encode(dump).decode('ascii')

        # Send data
        counter = itertools.count(0)
        response = None
        while next(counter) <= self._RETRY_COUNT:
            # Try to send data
            try:
                response = api.post(
                    self._CONNECTION_API_URL.format(self._connection_id),
                    {'data': serialized},
                )
                break
            except WebApiError as e:
                error_name = e.error['name']
                Logger.warn('App communication is not available because of "{}".'.format(error_name))
                if error_name not in ['IllegalStateException', 'AppServerAccessException', 'DataNotFoundException']:
                    raise

            # Retry to establish connection
            self._connection_id = self._establish_connection(self._api_token)
            Logger.warn('App communication is re-opened using connection ID "{}".'.format(self._connection_id))

        if response is None:
            # Request failed even if tried to re-connect
            raise CommunicationError('App communication is not available.')

        Logger.info('Request data is sent via communication and response data is received.')

        # Recover serialized response data
        serialized = response['data']
        dump = base64.b64decode(serialized.encode('ascii'))
        response = pickle.loads(dump)

        return response

    @classmethod
    def _establish_connection(cls, api_token):
        """Tries to establish communication connection."""
        api = WebApi(api_token)
        try:
            response = api.post(cls._OPEN_API_URL, {
                'address': 'localhost',  # 'localhost' is necessary
                'app_id': '',  # Empty value is necessary
            })
        except WebApiError as e:
            if e.error['name'] == 'AppServerAccessException':
                raise CommunicationError('Client side cannot access to background app.')
            else:
                raise

        return response['connection_id']
