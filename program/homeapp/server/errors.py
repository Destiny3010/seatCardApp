# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from enum import Enum


class ErrorCode(Enum):
    """This enum defines application error code."""
    Undefined = 0
    InvalidRequest = 1
    CommunicationFailed = 2
    PrintJobCannotStarted = 3


class AppError(Exception):
    """This class represents a request handling error."""

    def __init__(self, error_code, status_code, details=None):
        """Initializes a new instance.

        Args:
            error_code (ErrorCode): Error code.
            status_code (int): HTTP status code.
            details (dict): Detail information.
        """
        super().__init__()

        self.error_code = error_code
        self.status_code = status_code
        self.details = details


class BadRequestError(AppError):
    """This class represents a bad request error."""

    def __init__(self, error_code, details=None):
        super().__init__(error_code, status_code=400, details=details)


class NotFoundError(AppError):
    """This class represents a not found error."""

    def __init__(self, error_code, details=None):
        super().__init__(error_code, status_code=404, details=details)


class ServerError(AppError):
    """This class represents a server side error."""

    def __init__(self, error_code, details=None):
        super().__init__(error_code, status_code=500, details=details)
