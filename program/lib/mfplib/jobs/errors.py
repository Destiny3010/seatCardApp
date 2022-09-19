# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.


class JobError(Exception):
    """This class represents a job error."""
    pass


class InvalidParameterError(JobError):
    """This class represents an invalid job parameter error."""
    def __init__(self, message=None):
        super().__init__(message or 'Job parameter is invalid.')


class DisabledFunctionError(JobError):
    """This class represents a disabled function error."""
    def __init__(self, message=None):
        super().__init__(message or 'Setting is disabled to start a job.')


class PermissionError(JobError):
    """This class represents a user permission insufficient error."""
    def __init__(self, message=None):
        super().__init__(message or 'User permission is insufficient to start a job.')


class QuotaEmptyError(JobError):
    """This class represents a user quota empty."""
    def __init__(self, message=None):
        super().__init__(message or 'Quota is empty.')


class RunningOtherServiceError(JobError):
    """This class represents a running other service error."""
    def __init__(self, message=None):
        super().__init__(message or 'Job cannot be start because other service is running.')


class JobTimeoutError(JobError):
    """This class represents an app job timeout error."""
    def __init__(self, message=None):
        super().__init__(message or 'App job is not completed in timeout.')


class JobCanceledError(JobError):
    """This class represents an app job canceled error."""
    def __init__(self, message=None):
        super().__init__(message or 'App job is canceled by user request.')


class StorageFullError(JobError):
    """This class represents a storage full error."""
    def __init__(self, message=None):
        super().__init__(message or 'Device storage is full.')
