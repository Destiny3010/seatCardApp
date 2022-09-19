# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from ...webapi import WebApi
from ...debug import Logger


class ImageSourceRepository:
    """This class manages image source repository."""

    _KEEP_API_URL = '/jobs/scan/scan_to_app/keep_appconv_files'
    _FILES_API_URL = '/jobs/appconv/files'

    def __init__(self, api_token):
        """Initializes a new instance.

        Args:
            api_token (str): API access token.
        """
        self._api = WebApi(api_token)

    def switch_keep_mode(self, enabled=True):
        """Switches keep mode of image sources.

        Initially, all image sources are deleted automatically when home app is started.
        But once keep mode is enabled, existing image files will be kept (not deleted) regardless home app operation.

        Args:
            enabled (bool): Keep mode is enabled or not.
        """
        self._api.patch(self._KEEP_API_URL, {'keep_appconv_file': enabled})
        Logger.info('Keep mode of image sources is switched (keep sources: {})'.format(enabled))

    def fetch(self, file_name):
        """Gets sources of image processing.

        Args:
            file_name (str): File name of image sources. This is passed in start method of ImageProcessingScanJob class.
        Returns:
            list[str]: Image source names.
        """
        response = self._api.get(self._FILES_API_URL)
        files = response['storage_path_list']

        files = filter(lambda x: x.startswith(file_name), files)
        files = sorted(files, key=lambda x: x)

        Logger.debug('Image sources (count: {}) are fetched.'.format(len(files)))
        return files

    def delete(self, sources):
        """Deletes sources of image processing.

        Args:
            sources (list[str]): Source names.
        """
        SIZE = 50
        gen = (sources[i: i + SIZE] for i in range(0, len(sources), SIZE))
        for targets in gen:
            self._api.delete(self._FILES_API_URL, {'storage_path_list': ','.join(targets)})

        Logger.debug('Image sources (count: {}) are deleted.'.format(len(sources)))

    def delete_all(self):
        """Deletes all sources of image processing."""
        self._api.delete(self._FILES_API_URL)
        Logger.debug('All image sources are deleted.')
