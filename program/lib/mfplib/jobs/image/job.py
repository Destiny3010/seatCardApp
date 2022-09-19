# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from ..job import Job
from ..appjob import AppJobListener
from ..errors import (
    InvalidParameterError,
    DisabledFunctionError,
    RunningOtherServiceError,
    JobCanceledError,
    StorageFullError,
)
from ...webapi import WebApiError
from ...debug import Logger


class ImageFileFormatter:
    """This class creates image files from scan job result."""

    def __init__(self, api_token):
        """Initializes a new instance.

        Args:
            api_token (str): API access token.
        """
        self._api_token = api_token

    def create_image_files(self, sources, file_name, format, ocr=None, output_dir=''):
        """Creates image files from scan job result.

        Args:
            sources (list[str]): Sources of image files.
            file_name (str): Output file name.
            format (ImageFileFormat): Image file format.
            ocr (OcrSetting): OCR setting.
            output_dir (str): Output directory path.
        Raises:
            InvalidParameterError: Setting value is invalid.
            DisabledFunctionError: Scan setting is disabled or installed scan license is insufficient.
            JobTimeoutError: Job is not completed in timeout.
            JobCanceledError: Running job is canceled by user request.
            RunningOtherServiceError: Scan job cannot be started because of other services running.
            StorageFullError: Internal storage is full.
        """
        if not len(sources):
            raise ValueError('Specified sources are empty.')

        # Start job
        listener = AppJobListener()
        job = FormatJob.start(
            api_token=self._api_token,
            sources=sources,
            file_name=file_name,
            file_format=format,
            ocr=ocr,
            output_dir=output_dir,
            listener=listener,
        )
        event = listener.listen()
        status, reason = event.status, event.reason

        if status == 'completed' and reason == 'success':
            # App job is completed successfully
            Logger.warn('Image file creating job (ID: {}, format: {}) is completed.'.format(job.id, format.value))
        else:
            # App job failed
            Logger.warn('Failed to format image file (job ID: {}, reason: {}).'.format(job.id, reason))

            error = {
                'user_request': JobCanceledError,
                'hard_disk_full': StorageFullError,
            }.get(reason, None)

            if error:
                raise error()
            else:
                raise RuntimeError('Unexpected app job event is received (reason: {}).'.format(reason))


class FormatJob(Job):
    """This class handles image file creating job."""

    _API_URL = '/jobs/appconv'

    @classmethod
    def start(
            cls,
            api_token,
            sources,
            file_name,
            file_format,
            ocr=None,
            output_dir='',
            listener=None):
        """Starts a job which creates image files from scan job result."""
        # Build parameter
        parameter = cls._build_parameter(sources, file_name, output_dir, file_format, ocr)

        # Start job
        listener = AppJobListener() if listener is None else listener
        try:
            job_id = super().start(api_token, cls._API_URL, parameter, listener)
        except WebApiError as e:
            error = {
                'JobParameterException': InvalidParameterError,
                'DisableFunctionException': DisabledFunctionError,
                'RunningOtherServiceException': RunningOtherServiceError,
                'FileStorageFullException': StorageFullError,
            }.get(e.error['name'], None)

            if error:
                raise error()
            else:
                raise

        Logger.warn('New image file job is started by job ID "{}".'.format(job_id))
        return cls(api_token, job_id)

    @classmethod
    def _build_parameter(cls, sources, file_name, output_dir, file_format, ocr=None):
        """Builds job parameter."""
        parameter = {
            'appconv_input_parameter': {
                'input_file_name_list': sources,
            },
            'appconv_storage_parameter': {
                'output_file_format': file_format.value,
                'output_file_name': file_name,
                'storage_path': output_dir,
            },
            'auto_adjust': True,
            'auto_event': True,
        }

        if file_format.is_ocr_necessary() and ocr:
            ocr_settings = {
                'primary_language': ocr.primary_language.value,
                'secondary_language': ocr.secondary_language.value,
            }
            if ocr.auto_rotation is not None:
                ocr_settings['autorotation_enabled'] = ocr.auto_rotation

            parameter['appconv_ocr_parameter'] = {
                'enabled': True,
                'ocr_settings': ocr_settings,
            }

        return parameter
