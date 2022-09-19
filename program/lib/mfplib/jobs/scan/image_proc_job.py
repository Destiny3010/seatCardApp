# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from .job import ScanJob
from ...debug import Logger


class ImageProcessingScanJob(ScanJob):
    """This class handles scan job using image processing (e.g. barcode recognition)."""

    @classmethod
    def start(cls, api_token, setting, file_name, listener=None):
        """Starts a new image processing scan job .

        Args:
            api_token (str): API access token.
            setting (ScanSetting): Scan setting.
            file_name (str): File name for image processing.
            listener (ScanJobListener): Scan job listener to handle scan event.
                If this argument is None, default scan job listener will be used.
                This default listener notifies scan events to client side.
        Returns:
            ScanJob: Started scan job.
        Raises:
            InvalidParameterError: Setting value is invalid.
            DisabledFunctionError: Scan setting is disabled or installed scan license is insufficient.
            PermissionError: Login user permission are not enough to start a scan job.
            QuotaEmptyError: Login user quota is empty to start a scan job.
            RunningOtherServiceError: Scan job cannot be started because of other services running.
            StorageFullError: Device storage is full.
        Note:
            Started scan job does not create image files in app storeage.
            Created image files are stored in temporary working area.
            To create image files, it is necessary to ImageFileFormatter class.

            Here, passed image file format is ignored in this method
            because the ImageFileFormatter class receives an image file format.
        """
        job = super()._start(api_token, setting, file_name, listener=listener, image_proc=True)
        Logger.warn('New image processing scan job is started by job ID "{}".'.format(job.id))

        return job
