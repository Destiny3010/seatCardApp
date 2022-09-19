# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from enum import Enum
from collections import namedtuple
import json
from ..webapi import WebApi, WebApiError


class _AppConfigType(Enum):
    """This enum specifies an app config item type."""
    Text = 'string'
    """Text type config item."""

    Boolean = 'boolean'
    """Boolean type config item."""

    Int = 'int'
    """Int type config item."""

    Float = 'float'
    """Float type config item."""


class AppConfigItem:
    """This class defines an app config item."""

    def __init__(self, name, type, initial_value):
        """Initializes a new instance."""
        self.name = name
        self.type = type
        self.initial_value = initial_value

    @classmethod
    def text(cls, name=None, initial_value=''):
        """Defines a text config item.

        Args:
            name (str): Config item name.
                If ``None`` is given, attribute name of ``Appconfig`` subclass is used.
            initial_value (str): Initial value.
        """
        return AppConfigItem(name, _AppConfigType.Text, initial_value)

    @classmethod
    def boolean(cls, name=None, initial_value=False):
        """Defines a boolean config item.

        Args:
            name (str): Config item name.
                If ``None`` is given, attribute name of ``Appconfig`` subclass is used.
            initial_value (bool): Initial value.
        """
        return AppConfigItem(name, _AppConfigType.Boolean, initial_value)

    @classmethod
    def int(cls, name=None, initial_value=0):
        """Defines an int config item.

        Args:
            name (str): Config item name.
                If ``None`` is given, attribute name of ``Appconfig`` subclass is used.
            initial_value (int): Initial value.
        """
        return AppConfigItem(name, _AppConfigType.Int, initial_value)

    @classmethod
    def float(cls, name=None, initial_value=0.):
        """Defines a float config item.

        Args:
            name (str): Config item name.
                If ``None`` is given, attribute name of ``Appconfig`` subclass is used.
            initial_value (float): Initial value.
        """
        return AppConfigItem(name, _AppConfigType.Float, initial_value)


_AppConfigItemSpec = namedtuple(
    'AppConfigItemSpec', ('attr_name', 'item_name', 'type', 'initial_value'))


class AppConfigError(Exception):
    """This class represents an app config error."""
    pass


class AppConfig:
    """This class manages app config.
    Sub class of ``AppConfig`` class fetches or stores app config sections.
    """

    _CONFIG_API_URL = '/app/config'
    _CONFIG_LIST_API_URL = '/app/config/list'

    _cached_specs = None

    def __init__(self, **kwargs):
        """Initializes a new instance."""
        # Set specified values in attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Get specified config specs
        specs = self.__class__._list_specs()

        # Set config item attributes which is not passed from args
        for spec in specs:
            if spec.attr_name not in kwargs:
                setattr(self, spec.attr_name, spec.initial_value)

    @classmethod
    def load_section(cls, api_token, section):
        """Loads an app config section.

        Args:
            api_token (str): API access token.
            section (str): App config section name.
        Returns:
            AppConfig: AppConfig object which attributes are fetched item values.
        Raises:
            AppConfigError: Section name or item name is not found, or item type is incorrect.
        """
        return cls.load_sections(api_token, [section])[0]

    @classmethod
    def load_sections(cls, api_token, sections):
        """Loads multiple app config sections.

        Args:
            api_token (str): API access token.
            sections (list[str]): App config section names.
        Returns:
            list[AppConfig]: AppConfig objects which attributes are fetched item values.
        Raises:
            AppConfigError: Section name or item name is not found, or item type is incorrect.
        """
        # Get config specs
        specs = cls._list_specs()

        # Return empty object if no config item is found
        if len(specs) == 0:
            return [cls()]

        # Build API parameter
        entries = [
            {'section': section, 'name': spec.item_name, 'type': spec.type.value}
            for section in sections for spec in specs
        ]

        # Load values from app config
        api = WebApi(api_token)
        try:
            response = api.get(cls._CONFIG_LIST_API_URL, {'config_entries': json.dumps(entries)})
        except WebApiError as e:
            if e.error['name'] == 'IllegalArgumentException':
                raise AppConfigError('Config section, item name or item type is invalid.')
            else:
                raise

        # Assign loaded values
        values = (item['value'] for item in response['app_config_list'])

        configs = []
        for section in sections:
            config = cls()

            for spec in specs:
                setattr(config, spec.attr_name, next(values))

            configs.append(config)

        return configs

    def save_section(self, api_token, section):
        """Saves current attribute values into an app config section.

        Args:
            api_token (str): API access token.
            section (str): Section name.
        Raises:
            AppConfigError: Section name or item name is not found, or item type is incorrect.
        Note:
            If attribute value is None, the config item is not updated.
        """
        # Get specified config specs
        specs = self._list_specs()

        # Skip if no config item
        if len(specs) == 0:
            return

        # Save all values
        api = WebApi(api_token)
        for spec in specs:
            # Get attribute value
            value = getattr(self, spec.attr_name)

            # Skip if attribute value is None or attribute is not present
            if value is None or type(value) is AppConfigItem:
                continue

            try:
                api.post(self._CONFIG_API_URL, {
                    'section': section,
                    'name': spec.item_name,
                    'type': spec.type.value,
                    'value': value,
                })
            except WebApiError as e:
                if e.error['name'] in ['IllegalArgumentException', 'value']:
                    raise AppConfigError('Config section, item name or item type is invalid.')
                else:
                    raise

    @classmethod
    def _list_specs(cls):
        """Lists up config item specifications which are defined by AppConfigItem.

        Returns:
            list[_AppConfigItemSpec]: App config item specifications.
        """
        if cls is AppConfig:
            return []

        if cls._cached_specs is not None:
            # Return cached specs
            return cls._cached_specs

        # Get all items of this class
        members = vars(cls)
        specs = [
            _AppConfigItemSpec(
                attr_name=name,
                item_name=value.name if value.name else name,  # Use attribute name if config name is not specified in AppConfigItem.name
                type=value.type,
                initial_value=value.initial_value,
            )
            for name, value in members.items() if type(value) is AppConfigItem
        ]

        # Cache retrieved items
        cls._cached_specs = specs
        return specs
