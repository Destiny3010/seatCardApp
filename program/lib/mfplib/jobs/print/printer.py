# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from collections import namedtuple

from .setting import (
    PrintSetting,
    PaperSize,
    ColorMode,
    TonerMode,
    DuplexMode,
    StaplePosition,
    HolePunchPosition,
    ScalingType,
)
from ...webapi import WebApi
from ...debug import Logger


class PrinterCapability(namedtuple('PrinterCapability', (
        'duplex_available',
        'stapler_available',
        'hole_puncher_available',
        'color_available',
        'erasable_blue_available'))):
    """This class represents a printer capability.

    Attributes:
        duplex_availabe (bool): Duplex print is available or not.
        stapler_available (bool): Stapler is available or not.
        hole_puncher_available (bool): Hole puncher is available or not.
        color_available (bool): Color print is available or not.
        erasable_blue_available (bool): Erasable blue print is available or not.
    """

    _CAPABILITY_API_URL = '/mfpdevice/capability/printer'

    _cache = None

    @classmethod
    def get_capability(cls, api_token):
        """Gets printer capability.

        Returns:
            PrinterCapability: Printer capability.
        """
        if cls._cache is not None:
            # Return cached capability if existing
            return cls._cache

        # Get capabilities
        api = WebApi(api_token)
        values = api.get(cls._CAPABILITY_API_URL, {'field': ','.join([
            'has_adu',
            'has_stapler',
            'has_hole_puncher',
            'supported_colors',
            'is_erasableblue',
        ])})

        # Build capability
        capability = PrinterCapability(
            duplex_available=values['has_adu'],
            stapler_available=values['has_stapler'],
            hole_puncher_available=values['has_hole_puncher'],
            color_available=values['supported_colors'],
            erasable_blue_available=values['is_erasableblue'],
        )

        cls._cache = capability
        return cls._cache


class Printer:
    """This class manages a printer."""

    _CAPABILITY_API_URL = '/mfpdevice/capability/printer'
    _SYSTEM_SETTING_API_URL = '/setting/controllers/system'
    _FUNC_SETTING_API_URL = '/setting/controllers/function'
    _PRINT_API_URL = '/jobs/print/direct_print'

    def __init__(self, api_token):
        """Initializes a new instance.

        Args:
            api_token (str): API access token.
        """
        self._api = WebApi(api_token)

    def get_capability(self):
        """Gets printer capability.

        Returns:
            PrinterCapability: Printer capability.
        """
        return PrinterCapability.get_capability(self._api.api_token)

    def is_finishing_unavailable_for_erasable_blue(self):
        """Gets whether finishing is unavailable or not for erasable blue print.

        If True is returned, finishing is not available for erasable blue print.
        Because stapled or punched sheet is not available for eraser device.

        Returns:
            bool: Finishing is unavailable or not for erasable blue print.
        """
        key = 'print_erasableblue_finishing_is_enabled'
        values = self._api.get(self._FUNC_SETTING_API_URL, {'field': key})
        unavailable = True if values[key] is False else False

        Logger.debug('Finishing unavailable for erasable blue: {}'.format(unavailable))
        return unavailable

    def is_external_counter_used(self):
        """Gets whether external counter (such as coin controller) is used or not.

        Returns:
            bool: External counter is used or not.
        """
        # Get setting about external counter used
        key = 'externalcounter_print_is_available'
        values = self._api.get(self._SYSTEM_SETTING_API_URL, {'field': key})
        used = values[key]

        Logger.debug('External counter used: {}'.format(used))
        return used

    def is_auto_color_unavailable_by_external_counter(self):
        """Gets whether auto color print is unavailable or not.

        If True is returned, auto color mode is not available.
        Because current external counter cannot switch charges based on print color mode.

        Returns:
            bool: Auto color print is unavailable or not.
        """
        key = 'type_of_external_counter'
        response = self._api.get(self._CAPABILITY_API_URL, {'field': key})
        counter_type = response[key]

        key = 'externalcounter_print_is_available'
        response = self._api.get(self._SYSTEM_SETTING_API_URL, {'field': key})
        counter_used = response[key]

        # Specify auto color unavailable or not
        unavailable_counters = ['coincontroller']
        unavailable = counter_used and counter_type in unavailable_counters

        Logger.debug('Auto color unavailability: {}, external counter: {}'.format(unavailable, counter_type))
        return unavailable

    def get_supported_paper_sizes(self):
        """Gets supported paper sizes.

        Returns:
            list[str]: Supported paper sizes.
        """
        key = 'papersize_supported_papersizes'
        values = self._api.get(self._CAPABILITY_API_URL, {'field': key})
        values = values[key]

        all_sizes = [size.value for size in PaperSize]

        paper_sizes = []
        for value in values:
            value = value[:-2] if value.endswith('_r') else value  # Cut '_r'

            if value in all_sizes and value not in paper_sizes:
                paper_sizes.append(value)

        paper_sizes = [PaperSize(size) for size in paper_sizes]

        return paper_sizes

    def get_default_setting(self):
        """Retrieves current default print setting.

        Returns:
            PrintSetting: Default print setting.
        """
        # Get default setting
        parameter = self._api.get(self._PRINT_API_URL)

        # Parse response
        job_parameter = parameter['print_job_parameters']
        print_parameter = job_parameter['print_parameter']
        image_parameter = print_parameter['print_image_adjustment']

        setting = PrintSetting(
            sets=print_parameter['set'],
            paper_size=PaperSize.parse(image_parameter['paper_size']),
            color_mode=ColorMode.parse(image_parameter['print_color_mode']),
            toner_mode=TonerMode.parse(image_parameter['toner_mode']),
            duplex_mode=DuplexMode.parse(print_parameter['print_duplex_type']),
            staple=StaplePosition.parse(print_parameter['print_staple_position']),
            hole_punch=HolePunchPosition.parse(print_parameter['print_hole_punch_position']),
            original_size_prioritized=image_parameter['prioritize_original_size'],
            scaling_type=ScalingType.parse(image_parameter['print_scaling_type']),
        )

        return setting
