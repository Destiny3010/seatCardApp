# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

"""This module implements WebApi class."""

import json
from requests import Session


class WebApiError(Exception):
    """This class represents an API error."""

    def __init__(self, status_code=500, errors=None):
        self._status_code = status_code
        self._errors = [] if errors is None else errors

    @property
    def status_code(self):
        """Gets HTTP status code."""
        return self._status_code

    @property
    def errors(self):
        """Gets all errors."""
        return self._errors

    @property
    def error(self):
        """Gets first error in all them."""
        error = self._errors[0] if self._errors else {}
        return error

    def __str__(self):
        str = 'status_code: {0}, errors: {1}'.format(self._status_code, self._errors)
        return str


class WebApi:
    """This class sends an API request."""

    _ACCESS_TOKEN_HEADER = 'X-WebAPI-AccessToken'
    _BASE_URL = 'http://embapp-local.toshibatec.co.jp:50187/v1.0'

    _SESSION = Session()

    DEFAULT_TIMEOUT = 15.0

    def __init__(self, api_token):
        """Initializes a new instance.

        Args:
            api_token (str): API access token.
        """
        self._api_token = api_token
        self._headers = {self._ACCESS_TOKEN_HEADER: self._api_token}

    @property
    def api_token(self):
        """Gets an API access token."""
        return self._api_token

    def request(self, method, url, queries=None, payloads=None, timeout=None):
        """Requests API.

        Args:
            method (str): HTTP method.
            url (str): API URL.
            queries (dict): Request queries for HTTP GET and DELETE.
            payloads (dict): Request body for HTTP POST, PUT and PATCH.
            timeout (int): Access timeout by milli-seconds. If None is passed, DEFAULT_TIMEOUT is used.
        Returns:
            dict: Response body
        Raises:
            WebApiError: API returns errors.
        """
        response = self._SESSION.request(
            method,
            self._BASE_URL + url,
            headers=self._headers,
            params=queries,
            data=None if payloads is None else json.dumps(payloads),
            timeout=timeout or self.DEFAULT_TIMEOUT,
        )

        status_code = response.status_code
        body = response.json()

        if status_code >= 400:
            raise WebApiError(status_code, body['errors'])

        return body

    def get(self, url, queries=None, timeout=None):
        """Sends a request by HTTP GET.

        Args:
            url (str): API URL.
            queries (dict): Request queries.
            timeout (int): Access timeout by milli-seconds. If None is passed, DEFAULT_TIMEOUT is used.
        Returns:
            dict: Response body
        Raises:
            WebApiError: API returns errors.
        """
        return self.request('GET', url, queries=queries, timeout=timeout)

    def post(self, url, payloads=None, timeout=None):
        """Sends a request by HTTP POST.

        Args:
            url (str): API URL.
            payloads (dict): Request body.
            timeout (int): Access timeout by milli-seconds. If None is passed, DEFAULT_TIMEOUT is used.
        Returns:
            dict: Response body
        Raises:
            WebApiError: API returns errors.
        """
        return self.request('POST', url, payloads=payloads, timeout=timeout)

    def put(self, url, payloads=None, timeout=None):
        """Sends a request by HTTP PUT.

        Args:
            url (str): API URL.
            payloads (dict): Request body.
            timeout (int): Access timeout by milli-seconds. If None is passed, DEFAULT_TIMEOUT is used.
        Returns:
            dict: Response body
        Raises:
            WebApiError: API returns errors.
        """
        return self.request('PUT', url, payloads=payloads, timeout=timeout)

    def patch(self, url, payloads=None, timeout=None):
        """Sends a request by HTTP PATCH.

        Args:
            url (str): API URL.
            payloads (dict): Request body.
            timeout (int): Access timeout by milli-seconds. If None is passed, DEFAULT_TIMEOUT is used.
        Returns:
            dict: Response body
        Raises:
            WebApiError: API returns errors.
        """
        return self.request('PATCH', url, payloads=payloads, timeout=timeout)

    def delete(self, url, queries=None, timeout=None):
        """Sends a request by HTTP DELETE.

        Args:
            url (str): API URL.
            queries (dict): Request queries.
            timeout (int): Access timeout by milli-seconds. If None is passed, DEFAULT_TIMEOUT is used.
        Returns:
            dict: Response body
        Raises:
            WebApiError: API returns errors.
        """
        return self.request('DELETE', url, queries=queries, timeout=timeout)
