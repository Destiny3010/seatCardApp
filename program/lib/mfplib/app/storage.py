# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from enum import Enum
import itertools

from ..webapi import WebApi, WebApiError
from ..debug import Logger


class AppStorageType(Enum):
    """This enum represents an app storage type."""
    Normal = 'normal'
    Cloneable = 'clonable'


class AppStorageError(Exception):
    """This class represents an app storage error."""
    pass


class FileNotFoundError(AppStorageError):
    """This class represents a file or directory not found."""
    pass


class AppStorageFullError(AppStorageError):
    """This class represents an app storage is full."""
    def __init__(self, message=None):
        super().__init__(message or 'Device storage is full.')


class AppStorage:
    """This class manages an app storage."""

    _STORAGE_API_URL = '/app/storage/self'
    _DIR_API_URL = '/app/storage/self/directories'
    _FILE_API_URL = '/app/storage/self/files'

    _ITEMS_PER_PAGE = 50

    _root_paths = {}

    def __init__(self, api_token, type=AppStorageType.Normal):
        """Initializes a new instance.

        Args:
            api_token (str): API access token.
            type (AppStorageType): App storage type. Default is 'Normal'.
        """
        self._api = WebApi(api_token)
        self._type = type

    @property
    def type(self):
        """Gets app storage type."""
        return self._type

    def get_path(self, path=''):
        """Gets an absolute path.

        Args:
            path (str): App storage path (e.g. 'files/history.txt'). Default is root.
        Returns:
            str: Absolute path.
        """
        # Get cached root path
        root_path = AppStorage._root_paths.get(self._type, None)

        if root_path is None:
            # Gets root path using API if no cached
            response = self._api.get(self._STORAGE_API_URL, {'type': self._type.value})
            root_path = response['absolute_path']

            # Cache retrieved path
            AppStorage._root_paths[self._type] = root_path

        # Get absolute path
        abs_path = self._join(root_path, path)
        return abs_path

    def get_directories(self, parent_dir=''):
        """Gets directories under specified path.

        Args:
            parent_dir (str): Parent directory path in app storage. Default is root.
        Returns:
            list[str]: Sub directory names.
        Raises:
            FileNotFoundError: Specified parent directory path is not found.
        """
        dir_names = []
        try:
            counter = itertools.count(1)
            for page in counter:
                response = self._api.get(self._DIR_API_URL, {
                    'storage_type': self._type.value,
                    'parentdir': parent_dir,
                    'page': page,
                    'per_page': self._ITEMS_PER_PAGE,
                })
                dir_names += response['storage_path_list']

                if 'next' not in response:
                    return dir_names
        except WebApiError as e:
            Logger.warn('Parent directory path is not found.')
            error = {
                'IllegalArgumentException': FileNotFoundError('Parent directory path is not found.'),
            }.get(e.error['name'], None)

            if error:
                raise error
            else:
                raise

    def create_directory(self, dir_path):
        """Creates a new directory under root path.

        Args:
            dir_path (str): New directory path.
        Raises:
            ValueError: Directory path is not specified.
            FileNotFoundError: Directory path is not found.
            IOError: Failed to create a new directory.
            StorageFullError: Device storage is full.
        """
        if len(dir_path) == 0:
            raise ValueError('Directory path is not specified.')

        try:
            self._api.post(self._DIR_API_URL, {
                'storage_type': self._type.value,
                'storage_path': dir_path,
            })
        except WebApiError as e:
            Logger.warn('Failed to create a new directory in app storage.')
            error = {
                'FileNotFoundException': FileNotFoundError('Directory path is not found.'),
                'IOException': IOError('Failed to create a new directory.'),
                'FileStorageFullException': AppStorageFullError(),
            }.get(e.error['name'], None)

            if error:
                raise error
            else:
                raise

    def move_directory(self, src, dst=''):
        """Moves a directory in normal storage.

        Args:
            src (str): Source directory path.
            dst (str): Destination directory path. Default is root.
        Raises:
            ValueError: Source directory path is empty.
            FileNotFoundError: Destination path is invalid.
            IOError: Failed to move a directory.
            StorageFullError: Device storage is full.
        Note:
            Only normal storage can move a directory.
            Other types are not available and will raise IOError.
        """
        if len(src) == 0:
            raise ValueError('Source directory path is not specified.')

        if self._type is not AppStorageType.Normal:
            raise IOError('This storage type cannot move a directory.')

        try:
            self._api.patch(self._DIR_API_URL, {
                'from_path': src,
                'to_path': dst,
            })
        except WebApiError as e:
            error = {
                'FileNotFoundException': FileNotFoundError('Source directory path is not found.'),
                'IOException': IOError('Destination path is invalid.'),
                'FileStorageFullException': AppStorageFullError(),
            }.get(e.error['name'], None)

            if error:
                raise error
            else:
                raise

    def delete_directory(self, dir_path):
        """Deletes an existing directory.

        Args:
            dir_path (str): Target directory path.
        Raises:
            ValueError: Directory path is empty.
            IOError: Failed to delete a directory.
        Note:
            Even if specified directory path is not present, this method raises no error.
        """
        if len(dir_path) == 0:
            raise ValueError('Directory path is not specified.')

        try:
            self._api.delete(self._DIR_API_URL, {
                'storage_type': self._type.value,
                'dirpath': dir_path,
            })
        except WebApiError as e:
            if e.error['name'] == 'FileNotFoundException':
                Logger.warn('Directory path to be deleted is not found.')
                return  # Specified path is not present

            error = {
                'IOException': IOError('Failed to delete a directory.'),
            }.get(e.error['name'], None)

            if error:
                raise error
            else:
                raise

    def get_files(self, dir_path=''):
        """Gets file names in a directory.

        Args:
            dir_path (str): Directory path in app storage. Default is root.
        Returns:
            list[str]: File names in the directory.
        Raises:
            FileNotFoundError: Directory path is not found.
        """
        files = []
        try:
            counter = itertools.count(1)
            for page in counter:
                response = self._api.get(self._FILE_API_URL, {
                    'storage_type': self._type.value,
                    'parentdir': dir_path,
                    'is_recursive': False,
                    'page': page,
                    'per_page': self._ITEMS_PER_PAGE,
                })

                files += response['storage_path_list']

                if 'next' not in response:
                    return files
        except WebApiError as e:
            Logger.warn('Directory path is not found.')
            error = {
                'FileNotFoundException': FileNotFoundError('Directory path is not found.'),
            }.get(e.error['name'], None)

            if error:
                raise error
            else:
                raise

    def move_file(self, src, dst=''):
        """Moves a file in normal storage.

        Args:
            src (str): Source file path.
            dst (str): Destination file or directory path. Default is root directory.
        Raises:
            ValueError: Source path is empty.
            FileNotFoundError: Source file path is not found.
            IOError: Invalid storage type or destination path is invalid.
            StorageFullError: Device storage is full.
        Note:
            Only normal storage can move a file.
            Other storage types are not available and will raise IOError.
        """
        if len(src) == 0:
            raise ValueError('Source file path is not specified.')

        if self._type is not AppStorageType.Normal:
            raise IOError('This storage type cannot move a file.')

        try:
            self._api.patch(self._FILE_API_URL, {
                'from_path': src,
                'to_path': dst,
            })
        except WebApiError as e:
            error = {
                'FileNotFoundException': FileNotFoundError('Source file path is not found.'),
                'IOException': IOError('Destination path is invalid.'),
                'FileStorageFullException': AppStorageFullError(),
            }.get(e.error['name'], None)

            if error:
                raise error
            else:
                raise

    def delete_file(self, file_path):
        """Deletes a file.

        Args:
            file_path (str): Target file path.
        Raises:
            ValueError: File path is empty.
            IOError: Failed to delete a file.
        Note:
            Even if specified file path is not present, this method raises no error.
        """
        if len(file_path) == 0:
            raise ValueError('File path is not specified.')

        try:
            self._api.delete(self._FILE_API_URL, {
                'storage_type': self._type.value,
                'filepath': file_path,
            })
        except WebApiError as e:
            if e.error['name'] == 'FileNotFoundException':
                Logger.warn('File path to be deleted is not found.')
                return  # Specified path is not present

            error = {
                'IOException': IOError('Failed to delete a file.'),
            }.get(e.error['name'], None)

            if error:
                raise error
            else:
                raise

    @classmethod
    def _join(cls, path1, path2):
        """Joins path1 and path2 with delineater."""
        path = path1[:-1] if path1.endswith('/') else path1

        if path2:
            if path:
                path += path2 if path2.startswith('/') else '/' + path2
            else:
                path = path2[1:] if path2.startswith('/') else path2

            if path.endswith('/'):
                path = path[:-1]

        return path
