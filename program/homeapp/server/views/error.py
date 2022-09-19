# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

import traceback

from pyramid.view import view_config

from mfplib.debug import Logger

from .view import View
from ..errors import AppError


class ErrorView(View):
    """This class handles unhandled exceptions in views."""

    def __init__(self, error, request):
        super().__init__(request)
        self._error = error

    @view_config(context=Exception, renderer='json')
    def handle_error(self):
        """Handles all unhandled exceptions."""
        if issubclass(type(self._error), AppError):
            # Known error occurred
            return self.response.error(
                status_code=self._error.status_code,
                error_code=self._error.error_code,
                details=self._error.details,
            )
        else:
            # Unexpected error occurred
            Logger.error(traceback.format_exc())
            return self.response.error()
