# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.


class RequestHandler:
    """This class is an abstract communication request handler."""

    def __init__(self, api_token):
        """Initializes a new instance."""
        self._api_token = api_token

    @property
    def api_token(self):
        """Gets API access token."""
        return self._api_token

    def handle_request(self, request):
        """Handles a communication request and returns a response."""
        raise NotImplementedError('handle_request method is not implemented.')
