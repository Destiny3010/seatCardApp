# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from collections import namedtuple

from pyramid.response import Response

from mfplib.debug import Logger

from ..errors import ErrorCode


class Route(namedtuple('Route', ('name', 'method'))):
    """This class represents a route context.

    Attributes:
        name (str): Route name.
        method (str): Requested HTTP method.
    """

    def __str__(self):
        return '{} - {}'.format(self.name, self.method)


class ResponseBuilder:
    """This class builds a response."""

    def __init__(self, route):
        """Initializes a new instance.

        Args:
            route (Route): Requested route object.
        """
        self._route = route

    def ok(self, body=None, status_code=200):
        """Builds a successfull response."""
        Logger.debug('Response for route "{}" is returned successfully.'.format(self._route))
        return Response(status_code=status_code, json_body=body)

    def error(self, status_code=500, error_code=ErrorCode.Undefined, details=None):
        """Builds an error response."""
        Logger.warn('Error response for route "{}" is returned (error code: {}).'.format(self._route, error_code.name))
        return Response(
            status_code=status_code,
            json_body={
                'error_code': error_code.value,
                'error_details': {} if details is None else details,
            },
        )


class View:
    """This class represents an abstract view."""

    _API_TOKEN_KEY = 'X-WebAPI-AccessToken'
    _SESSION_CORE_KEY = '_SESSION_CORE'

    def __init__(self, request):
        self._request = request
        self._route = Route(name=request.matched_route.name, method=request.method)
        self._response = ResponseBuilder(self._route)

        # Retrieve API access token from request headers
        self._api_token = request.headers[self._API_TOKEN_KEY]

    @property
    def request(self):
        """Gets request object."""
        return self._request

    @property
    def response(self):
        """Gets response builder."""
        return self._response

    @property
    def api_token(self):
        """Gets Web API access token."""
        return self._api_token

    @property
    def session(self):
        """Gets session values as dictionary."""
        # Try to get inner session
        # Based on beaker session limitation, dictionary object is stored in beaker session
        key = self._SESSION_CORE_KEY
        if key not in self._request.session:
            self._request.session[key] = {}

        return self._request.session[key]
