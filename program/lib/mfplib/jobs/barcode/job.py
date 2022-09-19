# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from enum import Enum
from collections import namedtuple
from xml.etree import ElementTree

from ..job import Job
from ..appjob import AppJobListener
from ..errors import (
    InvalidParameterError,
    DisabledFunctionError,
    RunningOtherServiceError,
    JobCanceledError,
    StorageFullError,
)
from ...app.storage import AppStorage, AppStorageType
from ...webapi import WebApiError
from ...utilities.enum_fallback import fallback
from ...debug import Logger


@fallback('auto')
class BarcodeType(Enum):
    """This enum represents barcode type."""
    Auto = 'auto'
    Barcode_1D = 'barcode1_d'
    Barcode_2D = 'barcode2_d'
    Code39 = 'code39'
    Code93 = 'code93'
    Code128 = 'code128'
    Codabar = 'codabar'
    Iata = 'iata'
    Interleaved = 'interleaved'
    Industrial = 'industrial'
    Matrix = 'matrix'
    Ucc128 = 'ucc128'
    UpcA = 'upc_a'  # ucca in API
    UpcE = 'upc_e'  # ucce in API
    Patch = 'patch'
    Aztec = 'aztec'
    DataMatrix = 'data_matrix'
    MaxiCode = 'maxi_code'
    Pdf417 = 'pdf417'
    QrCode = 'qr_code'
    Ean8 = 'ean_8'
    Ean13 = 'ean_13'


class BarcodePage(namedtuple('BarcodePage', ('number', 'barcodes'))):
    """This class represents a page which includes barcodes.

    Attributes:
        number (int): Page number.
        barcodes (list[BarcodeData]): Recognized barcodes.
    """
    pass


class BarcodeData(namedtuple(
        'BarcodeDara', ('text', 'left', 'top', 'right', 'bottom'))):
    """This class represents a recognized barcode data.

    Attributes:
        text (str): Recognized data.
        left (int): Barcode left position in page.
        top (int): Barcode top position in page.
        right (int): Barcode right position in page.
        bottom (int): Barcode bottom position in page.
    """
    pass


class BarcodeDecoder:
    """This class decodes barcodes in scanned pages."""

    WORK_DIR = '_jobs_barcode'

    def __init__(self, api_token):
        """Initializes a new instance.

        Args:
            api_token (str): API access token.
        """
        self._api_token = api_token

    def decode(self, sources, barcode_type=BarcodeType.Auto, ocr=None):
        """Decodes barcodes in scanned pages.

        Args:
            sources (list[str]): Sources of image processing.
            barcode_type (BarcodeType): Barcode type.
            ocr (OcrSetting): OCR setting.
        Returns:
            list[BarcodePage]: Pages which includes recognized barcodes.
        Raises:
            InvalidParameterError: Setting value is invalid.
            DisabledFunctionError: Scan setting is disabled or installed scan license is insufficient.
            JobTimeoutError: Job is not completed in timeout.
            JobCanceledError: Running job is canceled by user request.
            RunningOtherServiceError: Scan job cannot be started because of other services running.
            StorageFullError: Internal storage is full.
        """
        if not len(sources):
            return []  # Empty result is returned for empty input

        # Specify output file
        file_name = sources[len(sources) - 1]  # xxxx-0003.tif
        result_file = file_name + '-Barcode.xml'
        result_file_path = '{}/{}'.format(self.WORK_DIR, result_file)

        storage = AppStorage(self._api_token, AppStorageType.Normal)
        try:
            # Start job
            self._start_job(sources, file_name, barcode_type, ocr)

            # Parse result XML file
            file_path = storage.get_path(result_file_path)
            result_pages = self._parse_result(file_path)
            Logger.debug('Barcode recognition is completed in scanned pages (page count: {})'.format(len(sources)))

            return result_pages

        finally:
            # Delete output result file
            storage.delete_file(result_file_path)

    def _start_job(self, sources, file_name, barcode_type, ocr):
        """Executes barcode recognition job."""
        listener = AppJobListener()
        job = BarcodeJob.start(
            api_token=self._api_token,
            sources=sources,
            file_name=file_name,
            barcode_type=barcode_type,
            ocr=ocr,
            output_dir=self.WORK_DIR,
            listener=listener,
        )
        event = listener.listen()
        status, reason = event.status, event.reason

        if status == 'completed' and reason == 'success':
            # App job is completed successfully
            Logger.warn('Barcode recognition job (ID: {}) is completed.'.format(job.id))
        else:
            # App job failed
            Logger.warn('Failed to recognize barcodes (job ID: {}, reason: {}).'.format(job.id, reason))

            error = {
                'user_request': JobCanceledError,
                'hard_disk_full': StorageFullError,
            }.get(reason, None)

            if error:
                raise error()
            else:
                raise RuntimeError('Unexpected app job event is received (reason: {}).'.format(reason))

    def _parse_result(self, file_path):
        """Parses decode result XML file."""
        with open(file_path, mode='r', encoding='utf-8') as file:
            content = file.read()

            root_elem = ElementTree.fromstring(content)
            info_elem = root_elem.find('barcodedata_info')

            return self._parse_page_elements(info_elem.findall('page'))

    def _parse_page_elements(self, page_elems):
        """Parses page elements in result XML."""
        pages = [
            BarcodePage(
                number=int(page_elem.get('no')),
                barcodes=self._parse_barcode_elems(page_elem.findall('block')),
            )
            for page_elem in page_elems
        ]
        return pages

    def _parse_barcode_elems(self, barcode_elems):
        """Parses barcode elements in result XML."""
        barcodes = [
            BarcodeData(
                text=self._parse_text_elem(barcode_elem.find('text')),
                left=int(barcode_elem.get('l')),
                top=int(barcode_elem.get('t')),
                right=int(barcode_elem.get('r')),
                bottom=int(barcode_elem.get('b')),
            )
            for barcode_elem in barcode_elems
        ]
        return barcodes

    def _parse_text_elem(self, text_elem):
        """Parses text element in result XML."""
        values = [elem.text for elem in text_elem.findall('Data')]
        count = len(values)

        if count == 1:
            return values[0]
        elif count == 2:
            return ''.join(values)
        elif count == 3:
            return values[1]
        else:
            return ''


class BarcodeJob(Job):
    """This class decodes barcodes in scanned documents."""

    _API_URL = '/jobs/appconv'

    @classmethod
    def start(
            cls,
            api_token,
            sources,
            file_name,
            barcode_type=BarcodeType.Auto,
            ocr=None,
            output_dir='',
            listener=None):
        """Starts a barcode recognition job from scan job result."""
        # Build parameter
        parameter = cls._build_parameter(
            sources=sources,
            file_name=file_name,
            output_dir=output_dir,
            barcode_type=barcode_type,
            ocr=ocr,
        )

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

        Logger.warn('New barcode job is started by job ID "{}".'.format(job_id))
        return cls(api_token, job_id)

    @classmethod
    def _build_parameter(
            cls, sources, file_name, output_dir, barcode_type=BarcodeType.Auto, ocr=None):
        """Builds job parameter."""
        # Specify barcode type with fallback
        barcode_type_value = {
            'upc_a': 'ucca',
            'upc_e': 'ucce',
        }.get(barcode_type.value, barcode_type.value)

        # Build parameter
        ocr_settings = {
            'barcode_output_enabled': True,
            'autorotation_enabled': False,
            'barcode_type_list': [barcode_type_value],
            'barcode_checkdigit_enabled': False,
            'barcode_supplement': 'auto',
            'barcode_with_startstop_code': False,
        }

        if ocr:
            ocr_settings['primary_language'] = ocr.primary_language.value
            ocr_settings['secondary_language'] = ocr.secondary_language.value

        parameter = {
            'appconv_input_parameter': {
                'input_file_name_list': sources,
            },
            'appconv_storage_parameter': {
                'output_file_name': file_name,
                'storage_path': output_dir,
            },
            'appconv_ocr_parameter': {
                'enabled': True,
                'ocr_settings': ocr_settings,
            },
            'auto_adjust': True,
            'auto_event': True,
        }

        return parameter
