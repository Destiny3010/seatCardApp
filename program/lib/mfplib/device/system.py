# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from collections import namedtuple
from enum import Enum

from ..utilities.enum_fallback import fallback
from ..webapi import WebApi
from ..debug import Logger


class SystemCapability(namedtuple('SystemCapability', (
        'ocr_available', 'scan_available', 'print_available'))):
    """This class represents a device system capability.

    Attributes:
        ocr_available (bool): OCR is available or not.
        scan_available (bool): Scan function is available or not.
        print_available (bool): Print function is available or not.
    """
    pass


class FunctionConfig(namedtuple('FunctionConfig', (
        'local_store_enabled', 'network_store_enabled'))):
    """This class represents a device function configuration.

    Attributes:
        local_store_enabled (bool): Device can store a file in internal storage or not.
        network_store_enabled (bool): Device can store a file into remote network storage or not.
    """
    pass


@fallback('unknown')
class DeviceStorageType(Enum):
    """This enum represents a device storage type."""
    Unknown = 'unknown'
    Hdd = 'hdd'
    Ssd = 'ssd'
    DeviceMemory = 'devicememory'


class System:
    """This class represents a device system."""

    _GENERAL_CAPABILITY_API_URL = '/mfpdevice/capability'
    _CONTROLLER_CAPABILITY_API_URL = '/mfpdevice/capability/controller'
    _SYSTEM_SETTING_API_URL = '/setting/controllers/system'
    _FUNCTION_SETTING_API_URL = '/setting/controllers/function'

    _cached_serial_number = None

    def __init__(self, api_token):
        """Initializes a new instance.

        Args:
            api_token (str): API access token.
        """
        self._api = WebApi(api_token)

    def get_host_name(self):
        """Gets device host name.

        Returns:
            str: Device host name.
        """
        key = 'host_name'
        values = self._api.get(self._GENERAL_CAPABILITY_API_URL, {'field': key})
        return values[key]

    def get_serial_number(self):
        """Gets device serial number.

        Returns:
            str: Device serial number.
        """
        if self._cached_serial_number is None:
            key = 'serial_no'
            values = self._api.get(self._GENERAL_CAPABILITY_API_URL, {'field': key})
            System._cached_serial_number = values[key]

        return self._cached_serial_number

    def get_locale(self):
        """Gets system locale.

        Returns:
            str: System locale (e.g. en_US).
        """
        key = 'system_locale'
        values = self._api.get(self._SYSTEM_SETTING_API_URL, {'field': key})
        locale = values[key]

        # Fix locale string (e.g. en_us -> en_US)
        splits = locale.split('_')
        splits_len = len(splits)
        if splits_len == 1:
            locale = locale.lower()
        elif splits_len == 2:
            locale = splits[0].lower() + '_' + splits[1].upper()

        Logger.debug('System locale "{}" is retrieved.'.format(locale))
        return locale

    def get_storage_type(self):
        """Gets device storage type.

        Returns:
            DeviceStorageType: Device storage type.
        """
        key = 'type_of_storage'
        values = self._api.get(self._CONTROLLER_CAPABILITY_API_URL, {'field': key})
        storage_type = DeviceStorageType.parse(values[key])

        Logger.debug('Device storage type "{}" is retrieved.'.format(storage_type.name))
        return storage_type

    def get_capability(self):
        """Gets system capabilities.

        Returns:
            SystemCapability: System capability.
        """
        keys = ','.join(['has_ocr', 'has_scan', 'has_print'])
        values = self._api.get(self._CONTROLLER_CAPABILITY_API_URL, {'field': keys})

        capability = SystemCapability(
            ocr_available=values['has_ocr'],
            scan_available=values['has_scan'],
            print_available=values['has_print'],
        )

        Logger.debug('System capability is retrieved {}.'.format(capability))
        return capability

    def get_function_config(self):
        """Gets a device function configuration.

        Returns:
            FunctionConfig: Device function configuration.
        """
        keys = ','.join(['save_as_hdd_is_enabled', 'save_to_network_is_enabled'])
        values = self._api.get(self._FUNCTION_SETTING_API_URL, {'field': keys})

        config = FunctionConfig(
            local_store_enabled=values['save_as_hdd_is_enabled'],
            network_store_enabled=values['save_to_network_is_enabled'],
        )

        Logger.debug('Device function configuration is retrieved {}.'.format(config))
        return config
