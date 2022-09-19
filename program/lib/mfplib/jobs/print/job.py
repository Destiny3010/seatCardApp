# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from ..job import Job
from ..errors import (
    InvalidParameterError,
    PermissionError,
    QuotaEmptyError,
    RunningOtherServiceError,
    StorageFullError,
)
from ...webapi import WebApiError
from ...debug import Logger


class PrintJob(Job):
    """This class represents a print job."""

    _PRINT_API_URL = '/jobs/print/direct_print'

    @classmethod
    def start(cls, api_token, setting, file_path):
        """Starts a new print job.

        Args:
            api_token (str): API access token.
            setting (PrintSetting): Print setting.
            file_path (str): Source file path in normal app storage.
        Returns:
            PrintJob: Started print job.
        Raises:
            InvalidParameterError: Setting value is invalid.
            PermissionError: Login user permission are not enough to start a print job.
            QuotaEmptyError: Login user quota is empty to start a print job.
            RunningOtherServiceError: Scan job cannot be started because of other services running.
            StorageFullError: Device storage is full.
        """
        # Build parameter
        parameter = cls._build_parameter(setting, file_path)

        # Start print job
        try:
            job_id = super().start(api_token, cls._PRINT_API_URL, parameter)
        except WebApiError as e:
            error = {
                'JobParameterException': InvalidParameterError,
                'PermissionException': PermissionError,
                'QuotaEmptyException': QuotaEmptyError,
                'FileStorageFullException': StorageFullError,
                'RunningOtherServiceException': RunningOtherServiceError,
            }.get(e.error['name'], None)

            if error:
                raise error()
            else:
                raise

        Logger.info('New print job is started by job ID "{0}".'.format(job_id))
        return cls(api_token, job_id)

    @classmethod
    def _build_parameter(cls, setting, file_path):
        """Builds a print parameter set for API argument."""
        image_parameter = {
            'paper_size': setting.paper_size.value,
            'print_color_mode': setting.color_mode.value,
            'toner_mode': setting.toner_mode.value,
            'prioritize_original_size': setting.original_size_prioritized,
            'print_scaling_type': setting.scaling_type.value,
        }

        print_parameter = {
            'set': setting.sets,
            'print_duplex_type': setting.duplex_mode.value,
            'print_staple_position': setting.staple.value,
            'print_hole_punch_position': setting.hole_punch.value,
            'output_tray': None,
            'print_fold_type': None,
            'print_mode_type': None,
            'print_sort_type': None,
            'print_image_adjustment': image_parameter,
        }

        input_parameter = {
            'input_file_name': file_path,
            'storage_type': 'app_storage',
        }

        job_parameter = {
            'input_storage_parameter': input_parameter,
            'print_parameter': print_parameter,
        }

        parameter = {
            'auto_adjust': True,
            'auto_event': False,
            'print_job_parameters': job_parameter,
        }

        return parameter

    def serialize(self):
        """Serializes this instance.

        Returns:
            dict: Serialized data of this instance.
        """
        serialized = {
            'id': self._id,
        }
        return serialized
