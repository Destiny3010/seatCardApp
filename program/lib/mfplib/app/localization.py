#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright(c) 2020 TOSHIBA TEC CORPORATION, All Rights Reserved.

import importlib

from ..webapi import WebApi
from ..debug import Logger


_KNOWN_LOCALES = {
    'zh_hant': 'zh_tw',
    'zh_hk': 'zh_tw',
    'zh_mo': 'zh_tw',
    'nb_no': 'no_no',
    'nn_no': 'no_no',
}


class Localizer:
    """This class loads localized messages for requested locales."""

    _API_URL = '/app/context/self/localization_data_list'

    _MODULE_DIR = 'localization'
    _MODULE_NAME = 'messages'

    def __init__(self, api_token, builtin_locales):
        """Initializes a new instance of Localizer class.

        Args:
            api_token (str): API access token.
            builtin_locales list[str]: Built-in locales which are bundled in app package.
        """
        if not builtin_locales:
            raise ValueError('Any built-in locale is not specified.')

        self._api = WebApi(api_token)
        self._builtin_locales = builtin_locales
        self._default_locale = builtin_locales[0]

    @property
    def builtin_locales(self):
        """Gets built-in locales."""
        return self._builtin_locales

    @property
    def default_locale(self):
        """Gets default locale which is first item in built-in locales."""
        return self._default_locale

    def get_messages(self, locales=None):
        """Gets localized messages for specified locales.

        Args:
            locales (list[str]): Locales (e.g. ['en-US', 'ja-JP'] or ['en_us', 'ja_jp]).
                Each locale allows both '_' and '-' separator, and ignores case.
        Returns:
            dict: Localized messages.
        Note:
            This method specify locale for localized messages based on below rules.

            - Find available locale for requested locales order based on below sub rules.
            - Find full matched locale name in built-in locales.
            - If not found, find full matched locale name in installed one except built-in.
            - If not found, find locale in installed one using known locale information (e.g. locale started with 'zh_Hant' is 'zh_TW').
            - If not found, find locale evaluating only language code.
            - If any locale is not found, first locale in built-in locales are used.
        """
        # Specify locale
        locales = [] if locales is None else locales
        locale = self._specify_locale(locales)

        # Load messages based on locale
        messages = self._load_messages(locale)
        Logger.debug('Localized messages are fetched based on locale {}.'.format(locale))

        # Fallback messages using default locale messages
        messages = self._fallback_messages(messages)

        return messages

    def _specify_locale(self, requested_locales):
        """Specify locale based on installed locales."""
        # Get installed locales including built-in
        installed_locales = self._get_installed_locales()

        # Setup locale map
        #  ['en-US', 'ja-JP'] -> {'en_us': 'en-US', 'ja_jp': 'js-JP'}
        locale_map = {
            self._normalize_locale_name(locale): locale
            for locale in installed_locales
        }

        # Setup language code map
        #  ['en_US', 'en_GB', 'ja_JP'] -> {'en': 'en_US', 'ja': 'ja_JP'}
        language_map = {}
        for locale in installed_locales:
            language = locale.split('_')[0].lower()
            if language not in language_map:
                language_map[language] = locale

        # Find locale
        for locale in requested_locales:
            Logger.debug('Try to find localized messages for locale {}.'.format(locale))
            locale = self._normalize_locale_name(locale)

            # Find locale from installed
            specified_locale = locale_map.get(locale, None)
            if specified_locale:
                Logger.debug('Localized locale {} is found from installed one.'.format(specified_locale))
                return specified_locale

            # Find locale using known list
            known_locale = self._find_from_known_locales(locale)
            specified_locale = locale_map.get(known_locale, None)
            if specified_locale:
                Logger.debug('Localized locale {} is found from known locales.'.format(specified_locale))
                return specified_locale

            # Find locale from installed by language code
            language = locale.split('_')[0]
            specified_locale = language_map.get(language, None)
            if specified_locale:
                Logger.debug('Localized locale {} is found by language code.'.format(specified_locale))
                return specified_locale

        # Any locale is not found
        Logger.debug('Localized messages are fetched from default locale {} because requested locales are not found.'.format(self._default_locale))
        return self._default_locale

    def _get_installed_locales(self):
        """Retrieves installed locales including builtin."""
        # Get installed locales
        response = self._api.get(self._API_URL)

        installed_locales = [
            entry['locale'] for entry in response['localization_data_list']
        ]

        # Sort locales (built-in locales are prioritized)
        locales = [locale for locale in self._builtin_locales]
        for locale in installed_locales:
            if locale not in locales:
                locales.append(locale)

        return locales

    def _load_messages(self, locale):
        """Loads specified locale messages dynamically."""
        path = '{0}.{1}.{2}'.format(self._MODULE_DIR, locale, self._MODULE_NAME)

        try:
            module = importlib.import_module(path)
            return module.message
        except Exception:
            Logger.error('Requested locale {} messages could not be loaded.'.format(locale))
            raise

    def _fallback_messages(self, messages):
        """Fallbacks fetched messages using default locale messages."""
        # Load default locale messages
        default_messages = self._load_messages(self._default_locale)

        # Fallback messages
        #  If fetched messages miss a key, default locale message will be used
        messages = {
            key: messages.get(key, message)
            for key, message in default_messages.items()
        }

        return messages

    @classmethod
    def _find_from_known_locales(cls, locale):
        """Finds locale from known locale list."""
        for known_locale, installed_locale in _KNOWN_LOCALES.items():
            if locale.startswith(known_locale):
                return installed_locale

        return None

    @classmethod
    def _normalize_locale_name(cls, locale):
        """Convert locale name.

        Note:
            Example: en-US -> en_us
        """
        return locale.replace('-', '_').lower()
