# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from enum import Enum
from ...webapi import WebApi


class FileStorageType(Enum):
    """This enum represents file storage type."""
    AppStorage = 'app_storage'
    UsbStorage = 'usb_storage'


class PrintFile:
    """This class represents a print target file."""

    _PASSWORD_REQUIRED_API_URL = '/jobs/print/input_storage/actions/check_password_requirement'
    _PASSWORD_VALIDATION_API_URL = '/jobs/print/input_storage/actions/validate_password'

    def __init__(self, api_token, path, storage_type=FileStorageType.AppStorage):
        """Initializes a new instance.

        Args:
            api_token (str): API access token.
            path (str): File path.
            storage_type (FileStorageType): File storage type.
        """
        self._api = WebApi(api_token)
        self._path = path
        self._storage_type = storage_type

    @property
    def path(self):
        """Gets file path."""
        return self._path

    @property
    def storage_type(self):
        """Gets file storage type."""
        return self._storage_type

    def is_password_required(self):
        """Checks whether this file needs password or not
        (e.g. secure PDF needs password to open).

        Returns:
            bool: Password is necessary or not.
        """
        response = self._api.post(self._PASSWORD_REQUIRED_API_URL, {
            'storage_type': self._storage_type.value,
            'file_path': self._path,
        })
        required = response['status']

        return required

    def validate_password(self, password):
        """Validates password for this secure file.

        Args:
            password (str): Password to handle secure file.
        Returns:
            bool: Specified password is valid or not.
        """
        response = self._api.post(self._PASSWORD_VALIDATION_API_URL, {
            'storage_type': self._storage_type.value,
            'file_path': self._path,
            'password': password,
        })
        valid = response['status'] == 'OK'

        return valid
