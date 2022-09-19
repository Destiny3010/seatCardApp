# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from collections import namedtuple
from enum import Enum

from .setting import (
    ScanSetting,
    OcrSetting,
    ImageFileFormat,
    ColorMode,
    Resolution,
    OriginalMode,
    ImageRotation,
    DuplexMode,
    ExposureLevel,
    BackgroundLevel,
    ContrastLevel,
    SharpnessLevel,
    OcrLanguage,
)
from ...app.framework import Version
from ...utilities.enum_fallback import fallback
from ...webapi import WebApi
from ...debug import Logger


@fallback('unknown')
class InputDeviceType(Enum):
    """This enum represents a scan input device type."""
    Unknown = 'unknown'
    Platen = 'platen'
    Radf = 'radf'
    Dsdf = 'dsdf'


class InputDevice(namedtuple('InputDevice', ('type', 'paper_size'))):
    """This class represents a current input device of scanner.

    Attributes:
        type (InputDeviceType): Scan input device type.
        paper_size (str): Paper size to be scanned.
    """

    _ADF_API_URL = '/mfpdevice/scanner/adf'
    _PLATEN_API_URL = '/mfpdevice/scanner/platen'

    @classmethod
    def get_current(cls, api_token):
        api = WebApi(api_token)

        # Specify DF type
        capability = ScannerCapability.get_capability(api_token)
        df_type = capability.df_type

        # Specify scan input device (DF or platen)
        device_type = InputDeviceType.Platen
        if df_type:
            # Check DF has paper or not
            response = api.get(cls._ADF_API_URL)
            if response['has_paper']:
                device_type = df_type

        Logger.debug('Scan input device type is {}.'.format(device_type.name))

        # Get paper size
        if device_type is InputDeviceType.Platen and capability.size_detectable_on_platen:
            response = api.get(cls._PLATEN_API_URL)
            paper_size = response['detected_oriented_paper_size']['paper_size']
        else:
            # DF scan or Platen cannot detect original size automatically
            paper_size = 'auto'

        Logger.debug('Scan paper size is {}.'.format(paper_size))
        return cls(device_type, paper_size)


class ScannerCapability(namedtuple('ScannerCapability', (
        'df_type', 'blue_original_available', 'size_detectable_on_platen', 'a3_supported'))):
    """This class represents a scanner capability.

    Attributes:
        df_type (InputDeviceType): DF type. If DF is not installed, None will be returned.
        blue_original_available (bool): Blue original is available or not.
        size_detectable_on_platen (bool): Original size detection on platen is available or not.
        a3_supported (bool): A3 original size is supported or not.
    """

    _SCANNER_API_URL = '/mfpdevice/capability/scanner'
    _PRINTER_API_URL = '/mfpdevice/capability/printer'
    _CONTROLLER_API_URL = '/mfpdevice/capability/controller'

    _cache = None

    @classmethod
    def get_capability(cls, api_token):
        """Gets scanner capability."""
        if cls._cache is not None:
            # Return cached capability if existing
            return cls._cache

        api = WebApi(api_token)

        # Get DF type
        keys = ','.join(['has_adf', 'type_of_adf'])
        response = api.get(cls._SCANNER_API_URL, {'field': keys})
        if response['has_adf']:
            df_type = InputDeviceType.parse(response['type_of_adf'])
        else:
            df_type = None

        # Get blue original availability
        key = 'is_erasableblue'
        response = api.get(cls._PRINTER_API_URL, {'field': key})
        blue_original_available = response[key]

        version = Version.get_current(api_token)
        if not version.is_older(2, 3, 0):
            # For L6.5 or later machine, get capabilities of size detection on platen and A3 supported
            # These devices support below new keys
            keys = ','.join(['has_auto_size_detection_for_platen', 'has_a3_papersize'])
            response = api.get(cls._CONTROLLER_API_URL, {'field': keys})

            size_detectable_on_platen = response['has_auto_size_detection_for_platen']
            a3_supported = response['has_a3_papersize']
        else:
            # Before L6.5, all devices support size detection on platen
            # Also all devices support A3 scan
            size_detectable_on_platen = True
            a3_supported = True

        # Build capability
        capability = cls(
            df_type=df_type,
            blue_original_available=blue_original_available,
            size_detectable_on_platen=size_detectable_on_platen,
            a3_supported=a3_supported,
        )

        cls._cache = capability
        return cls._cache


class Scanner:
    """This class represents a scanner."""

    _SETTING_API_URL = '/setting/controllers/scan'
    _SCAN_API_URL = '/jobs/scan/scan_to_app'

    def __init__(self, api_token):
        """Initializes a new instance.

        Args:
            api_token (str): API access token.
        """
        self._api = WebApi(api_token)

    def get_capability(self):
        """Gets scanner capability.

        Returns:
            ScannerCapability: Scanner capability.
        """
        return ScannerCapability.get_capability(self._api.api_token)

    def is_secure_pdf_enforced(self):
        """Gets whether secure PDF is enforced or not.

        Returns:
            bool: Secure PDF is enforced or not.
        """
        key = 'secure_pdf_forced_encryption_is_enabled'
        response = self._api.get(self._SETTING_API_URL, {'field': key})
        enforced = response[key]

        Logger.debug('Secure PDF is enforced or not: {}.'.format(enforced))
        return enforced

    def get_default_original_mode(self, color_mode):
        """Gets default original modes for given color mode.

        Args:
            color_mode (~mfplib.jobs.scan.ColorMode): Color mode.
        Returns:
            OriginalMode: Original mode for given color mode.
        """
        key = {
            ColorMode.Auto: 'default_original_mode_color',
            ColorMode.FullColor: 'default_original_mode_color',
            ColorMode.Black: 'default_original_mode_black',
        }.get(color_mode, None)

        if key is None:
            raise ValueError('Default original mode for {} color is not configured.'.format(color_mode.name))

        response = self._api.get(self._SETTING_API_URL, {'field': key})
        original_mode = OriginalMode.parse(response[key])

        Logger.debug('Default original mode for {} color is {}.'.format(color_mode.name, original_mode.name))
        return original_mode

    def get_default_size_on_platen(self):
        """Gets default original size on platen where device does not have size detection on platen.

        Returned sizes
            * a4
            * a5
            * letter
            * legal
            * statement
            * b5
            * folio
            * 13_legal
            * 85_sq
            * a6
            * 16k

        Returns:
            str: Default original size on platen.
        Note:
            If device does not support auto size detection on platen, None will be returned.
        """
        # Get size detection availability on platen
        capability = ScannerCapability.get_capability(self._api.api_token)

        if not capability.size_detectable_on_platen:
            # Get default original size on platen because size detection is not available
            key = 'platen_original_size'
            response = self._api.get(self._SETTING_API_URL, {'field': key})

            # a4, a5, letter, legal, statement, b5, folio, 13_legal, 85_sq, a6, 16k
            size = response[key]
            Logger.info('Default original size for platen is {}.'.format(size))

            size = size[:-2] if size.endswith('_r') else size  # Cut '_r'
            return size
        else:
            # Auto size detection is available on platen
            # So default original size on platen is not configured
            Logger.info('Default original size for platen is not configured because auto size detection is available.')
            return None

    def get_input_device(self):
        """Gets current scan input device.

        Returns:
            InputDevice: Current scan input device.
        """
        return InputDevice.get_current(self._api.api_token)

    def get_default_setting(self):
        """Retrieves current default scan setting.

        Returns:
            ScanSetting: Default scan setting.
        """
        # Get default setting
        parameter = self._api.get(self._SCAN_API_URL)

        # Parse parameter
        scan_parameter = parameter['scan_parameter']
        adjustment_parameter = scan_parameter['image_adjustment_parameter']

        storage_parameter = parameter['scan_to_app_storage_parameter']
        output_parameter = storage_parameter['file_output_method']
        ocr_parameter = storage_parameter.get('ocr_settings', None)

        setting = ScanSetting(
            file_format=ImageFileFormat.parse(output_parameter['output_file_format']),
            color_mode=ColorMode.parse(scan_parameter['scan_color_mode']),
            resolution=Resolution.parse(scan_parameter['scan_resolution']),
            original_mode=OriginalMode.parse(adjustment_parameter['image_mode']),
            image_rotation=ImageRotation.parse(adjustment_parameter['scan_rotation']),
            duplex_mode=DuplexMode.parse(scan_parameter['duplex_type']),

            preview=scan_parameter['generate_preview'],
            omit_blank_page=scan_parameter['omit_blank_page'],

            ocr=None if ocr_parameter is None else OcrSetting(
                primary_language=OcrLanguage.parse(ocr_parameter['primary_language']),
                secondary_language=OcrLanguage.parse(ocr_parameter['secondary_language']),
                auto_rotation=ocr_parameter['autorotation_enabled'],
            ),

            exposure=ExposureLevel.parse(adjustment_parameter['scan_exposure']),
            background=BackgroundLevel.parse(adjustment_parameter['background_adjustment']),
            contrast=ContrastLevel.parse(adjustment_parameter['contrast']),
            sharpness=SharpnessLevel.parse(adjustment_parameter['sharpness']),
        )

        return setting
