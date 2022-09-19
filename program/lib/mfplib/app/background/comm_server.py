# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

import pickle
import base64
import importlib

from ...webapi import WebApi
from ...debug import Logger


class CommunicationServer:
    """This class manages app communication on server side."""

    _SERVER_API_URL = '/app/communication/server'

    def __init__(self, api_token):
        self._api = WebApi(api_token)
        self._opened = False

    @property
    def opened(self):
        """Gets communication server is opened or not."""
        return self._opened

    def open(self):
        """Starts to receive app communication from client side."""
        self._api.post(self._SERVER_API_URL, {
            'is_different_address_allowed': False,
            'is_different_appid_allowed': False,
            'session_mode': 'client',
        })

        self._opened = True
        Logger.info('App communication is opened on server side.')

    def close(self):
        """Closes existing app communication."""
        if not self._opened:
            Logger.warn('App communication is already closed.')
            return

        self._api.delete(self._SERVER_API_URL)

        self._opened = False
        Logger.info('App communication is closed on server side.')

    def handle_requested_data(self, request_data, client_api_token):
        """Handles a requested data via app communication.

        Args:
            request_data (str): Requested data via app communication.
            client_api_token (str): API access token for client session.
        Returns:
            str: Serialized response data to client.
        """
        # Recover serialized request data
        dump = base64.b64decode(request_data.encode('ascii'))
        request = pickle.loads(dump)

        # Specify request handler
        handler_path = request['handler_path']

        index = handler_path.rindex('.')
        module_path = handler_path[:index]
        class_name = handler_path[index + 1:]
        Logger.debug('Remote request is handled by {} class in {} module.'.format(class_name, module_path))

        # Invoke request handler
        handler_class = self._get_handler(module_path, class_name)
        handler = handler_class(client_api_token)
        response = handler.handle_request(request['body'])

        # Serialize response data
        dump = pickle.dumps(response)
        serialized = base64.b64encode(dump).decode('ascii')

        return serialized

    def _get_handler(self, module_path, class_name):
        """Gets request handler."""
        try:
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError):
            raise RuntimeError('Requested handler {}.{} is not found.'.format(module_path, class_name))
