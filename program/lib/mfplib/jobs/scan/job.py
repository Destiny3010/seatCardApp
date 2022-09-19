# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

import copy

from .scanner import Scanner, InputDeviceType
from .listener import ScanJobListener
from .setting import ImageFileFormat
from ..job import Job
from ..errors import (
    InvalidParameterError,
    DisabledFunctionError,
    PermissionError,
    QuotaEmptyError,
    RunningOtherServiceError,
    StorageFullError,
)
from ...webapi import WebApi, WebApiError
from ...debug import Logger


class ScanJob(Job):
    """This class represents a scan job."""

    _SCAN_API_URL = '/jobs/scan/scan_to_app'

    _JOB_API_URL = '/jobs/scan/{}'
    _PARAM_API_URL = '/jobs/scan/{}/scan_to_app/parameter'
    _DF_CONTINUE_API_URL = '/jobs/scan/{}/actions/continue_adf_scanning'
    _PAGE_DELETE_API_URL = '/jobs/scan/{}/scanned/{}'

    _running_job = None

    def __init__(self, api_token, id, input_device_type, setting, **extra_setting):
        """Initializes a new instance."""
        super().__init__(api_token, id)
        self._input_device_type = input_device_type
        self._api = WebApi(api_token)
        self._setting = setting
        self._extra_setting = extra_setting

    @property
    def platen_scanned(self):
        """Gets scanned on platen or not."""
        return self._input_device_type is InputDeviceType.Platen

    @classmethod
    def get_job(cls, job_id):
        """Gets running scan job by ID.

        Args:
            job_id (int): Running job ID.
        Returns:
            ScanJob: Scan job. If job is not found, None will be returned.
        """
        running_job = cls._running_job
        if running_job and running_job.id == job_id:
            return running_job
        else:
            return None

    @classmethod
    def start(cls, api_token, setting, file_name, output_dir='', listener=None):
        """Starts a new scan job.

        Args:
            api_token (str): API access token.
            setting (ScanSetting): Scan setting.
            file_name (str): Scan file name.
            output_dir (str): Output directory path in normal app storage.
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
        """
        job = cls._start(api_token, setting, file_name, output_dir=output_dir, listener=listener)
        Logger.warn('New scan job is started by job ID "{}".'.format(job.id))

        return job

    def resume(self):
        """Resumes an existing scan job.

        Raises:
            QuotaEmptyError: Login user quota is empty to continue a scan job .
        """
        # Get current input device
        scanner = Scanner(self._api_token)
        input_device = scanner.get_input_device()

        # Validate setting
        self._validate(self._api_token, self._setting, self._extra_setting, input_device.type)

        # Update original size change if platen is used
        if input_device.type is InputDeviceType.Platen:
            self._update_paper_size(input_device.paper_size)
            Logger.debug('Paper size is changed to "{}" on platen.'.format(input_device.paper_size))

        # Resume suspended job
        try:
            self._api.patch(self._JOB_API_URL.format(self.id), {'job_action': 'resume'})
        except WebApiError as e:
            error = {'QuotaEmptyException': QuotaEmptyError()}.get(e.error['name'], None)

            if error:
                raise error
            else:
                raise

        # Update input device type
        self._input_device_type = input_device.type

        Logger.warn('Suspended scan job "{}" is resumed.'.format(self.id))

    def stop(self):
        """Stops a running scan job.

        Returns:
            bool: Scan is stopped or not.
        Note:
            In some cases, a running scan job cannot be stopped.
            In this case, this method returns False (means the scan job is not stopped).
            If scan job is not stopped, it's necessary to try to stop again by calling this method.
        """
        # Check specified job status
        status = self._get_job_status()
        if status == 'suspended':
            Logger.warn('Scan job "{}" has been already suspended.'.format(self.id))
            return True
        elif status is None:
            # Scan job is not found
            Logger.warn('Scan job "{}" is not found.'.format(self.id))
            return False
        elif status != 'running':
            # Scan job is not cancelable by other reason
            Logger.warn('Scan job "{}" is not cancelable because of "{}".'.format(self.id, status))
            return False

        # Try to stop running job
        Logger.debug('Scan job "{}" is running.'.format(self.id))
        try:
            self._api.patch(self._JOB_API_URL.format(self.id), {'job_action': 'stop'})
        except WebApiError as e:
            if e.error['name'] in ['IllegalStateException', 'InternalException']:
                # Ignore this error
                Logger.warn('"{}" occurs while stopping scan job.'.format(e.error['name']))
            else:
                raise

        Logger.warn("Running scan job '{0}' is stopped.".format(self.id))
        return True

    def cancel(self):
        """Cancels a suspended scan job."""
        try:
            self._api.patch(self._JOB_API_URL.format(self.id), {'job_action': 'cancel'})
        except WebApiError as e:
            if e.error['name'] in ['IllegalStateException', 'InternalException']:
                # Ignore this error
                Logger.warn('Scan job is canceled forcibly.')
            else:
                raise

        Logger.warn('Suspended scan job "{}" is canceled.'.format(self.id))

    def finish(self):
        """Finishes a suspended scan job."""
        self._api.patch(self._JOB_API_URL.format(self.id), {'job_action': 'finish'})
        Logger.warn('Suspended scan job "{}" is finished.'.format(self.id))

    def continue_df_scanning(self):
        """Continues a running DF scan job not to finish after paper feeded.

        Returns:
            bool: Running DF scan job will be continued or not. If False is returned, job will not be continued.
        """
        if self._input_device_type is InputDeviceType.Platen:
            Logger.warn('Continuous request is not received because running scan job does not use DF.')
            return False

        try:
            self._api.post(self._DF_CONTINUE_API_URL.format(self.id))
            Logger.warn('After paper feeding, running DF scan job will be suspended to continue.')
            return True
        except WebApiError as e:
            if e.error['name'] == 'IllegalStateException':
                Logger.warn('Running DF scan job is not continuable.')
                return False
            else:
                raise

    def delete_page(self, page_number):
        """Deletes a scanned page.

        Args:
            page_number (int): Page number to be deleted.
        """
        self._api.delete(self._PAGE_DELETE_API_URL.format(self.id, page_number))
        Logger.warn('Scan page {} is deleted in job "{}".'.format(page_number, self.id))

    def serialize(self):
        """Serializes this instance.

        Returns:
            dict: Serialized data of this instance.
        """
        serialized = {
            'id': self.id,
            'platen_scanned': self.platen_scanned,
        }
        return serialized

    @classmethod
    def _start(
            cls,
            api_token,
            setting,
            file_name,
            output_dir=None,
            listener=None,
            **extra_setting):
        """Starts a new scan job.

        Args:
            api_token (str): API access token.
            setting (ScanSetting): Scan setting.
            file_name (str): Scan file name.
            output_dir (str): Output directory path in normal app storage.
            listener (ScanJobListener): Scan job listener to handle scan event.
        Returns:
            ScanJob: Started scan job.
        Note:
            ``extra_setting`` parameter supports:
                * image_proc (bool): App conv mode is enabled or not in scan job.
        """
        # Specify input device and paper size
        scanner = Scanner(api_token)
        device = scanner.get_input_device()

        # Validate setting
        cls._validate(api_token, setting, extra_setting, device.type)

        # Build parameter
        parameter = cls._build_parameter(setting, extra_setting, device, file_name, output_dir)

        # Start scan job
        listener = ScanJobListener() if listener is None else listener
        try:
            job_id = super().start(api_token, cls._SCAN_API_URL, parameter, listener)
        except WebApiError as e:
            error = {
                'JobParameterException': InvalidParameterError,
                'DisableFunctionException': DisabledFunctionError,
                'PermissionException': PermissionError,
                'QuotaEmptyException': QuotaEmptyError,
                'RunningOtherServiceException': RunningOtherServiceError,
                'FileStorageFullException': StorageFullError,
            }.get(e.error['name'], None)

            if error:
                raise error()
            else:
                raise

        # Cache started scan job
        job = cls(
            api_token=api_token,
            id=job_id,
            input_device_type=device.type,
            setting=copy.deepcopy(setting),
            **extra_setting,
        )
        ScanJob._running_job = job

        Logger.debug('New scan job is started by job ID "{}".'.format(job_id))
        return job

    @classmethod
    def _build_parameter(cls, setting, extra_setting, device, file_name, output_dir):
        """Builds a scan parameter set for API argument."""
        image_proc = extra_setting.get('image_proc', False)

        scan_parameter = {
            'scan_color_mode': setting.color_mode.value,
            'scan_resolution': setting.resolution.value,
            'duplex_type': setting.duplex_mode.value,
            'scan_paper_size': {
                'paper_size': device.paper_size,
            },
            'image_adjustment_parameter': {
                'image_mode': setting.original_mode.value,
                'scan_rotation': setting.image_rotation.value,
                'scan_exposure': setting.exposure.value,
                'background_adjustment': setting.background.value,
                'contrast': setting.contrast.value,
                'sharpness': setting.sharpness.value,
            },
            'generate_preview': setting.preview,
            'omit_blank_page': setting.omit_blank_page,
        }

        output_parameter = {
            'output_file_format': (
                ImageFileFormat.TiffSingle.value
                if image_proc else setting.file_format.value
            ),
            'file_name': file_name,
        }

        storage_parameter = {
            'file_output_method': output_parameter,
            'is_appconv_mode': image_proc,
        }
        if output_dir:
            storage_parameter['storage_path'] = output_dir

        ocr = setting.ocr
        if setting.file_format.is_ocr_necessary() and ocr:
            storage_parameter['ocr_settings'] = {
                'primary_language': ocr.primary_language.value,
                'secondary_language': ocr.secondary_language.value,
                'autorotation_enabled': ocr.auto_rotation,
            }

        parameter = {
            'auto_adjust': True,
            'auto_event': False,
            'scan_parameter': scan_parameter,
            'scan_to_app_storage_parameter': storage_parameter,
        }

        return parameter

    @classmethod
    def _validate(cls, api_token, setting, extra_setting, input_device_type):
        """Validates scan setting for current device state.

        If scan setting is not available, an error will raise.
        """
        pass

    def _get_job_status(self):
        """Gets specified job status."""
        try:
            response = self._api.get(self._JOB_API_URL.format(self.id))
            return response['job_status']['status']
        except WebApiError as e:
            if e.error['name'] == 'NotFoundException':
                return None
            else:
                raise

    def _update_paper_size(self, paper_size):
        self._api.patch(self._PARAM_API_URL.format(self.id), {
            'scan_parameter': {
                'scan_paper_size': {'paper_size': paper_size},
            },
        })
