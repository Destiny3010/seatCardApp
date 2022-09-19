# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from ...webapi import WebApi


_SESSION_API_URL = '/session/current'


def get_locale(api_token):
    """Gets display locale of home app session."""
    api = WebApi(api_token)
    response = api.get(_SESSION_API_URL)
    locale = response['display_language'].replace('-', '_')

    # Fix locale string (e.g. en_us -> en_US)
    splits = locale.split('_')
    splits_len = len(splits)
    if splits_len == 1:
        return locale.lower()
    elif splits_len == 2:
        return splits[0].lower() + '_' + splits[1].upper()
