# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from collections import namedtuple

from ..webapi import WebApi, WebApiError
from ..debug import Logger


class License(namedtuple(
        'License', ('trial_licensed', 'remaining_days', 'notification_required'))):
    """This class represents an app license.

    Attributes:
        trial_licensed (bool): License type is trial or not.
        remaining_days (int): Remaining days for trial license.
            If license type is not trial, this value will be 0.
        notification_required (bool): For trial license,
            notification (which alerts trial period is short) is necessary or not.
            If license type is not trial, this value will be always False.
    """

    _LIST_API_URL = '/app/unified_license/self'
    _TRIAL_API_URL = '/app/unified_license/trial/self'
    _THRESHOLD_API_URL = '/setting/controllers/license'

    @classmethod
    def get_status(cls, api_token):
        """Gets current license status.

        Args:
            api_token (str): API access token.
        Returns:
            License: License status. If app does not have any license, None will be returned.
        """
        api = WebApi(api_token)

        # Get authoritative license
        license = cls._get_authoritative_license(api)
        if license:
            # Authoritative license is installed
            Logger.warn('Authoritative app license has been activated.')
            return license

        # Get trial license
        license = cls._get_trial_license(api)
        if license:
            # Trial license is installed
            Logger.warn('Trial app license has been activated.')
            return license

        # Any license is not installed
        Logger.warn('Any app license is not installed.')
        return None

    @classmethod
    def _get_authoritative_license(cls, api):
        """Gets authoritative license."""
        response = api.get(cls._LIST_API_URL)
        items = response['unified_license_list']

        # Get authoritative or trial licenses
        for item in items:
            if item['is_activated'] and not item.get('is_trial', False):
                license = License(
                    trial_licensed=False,
                    remaining_days=0,
                    notification_required=False,
                )
                return license

        # Any authoritative license is not found.
        return None

    @classmethod
    def _get_trial_license(cls, api):
        """Gets trial license status."""
        # Get trial license status
        trial_licensed = False
        try:
            response = api.get(cls._TRIAL_API_URL)
            trial_licensed = response.get('is_activated', False)
        except WebApiError as e:
            # Any trial license is not found
            if e.error['name'] == 'DataNotFoundException':
                trial_licensed = False
            else:
                raise

        if not trial_licensed:
            # Activated trial license is not installed
            return None

        # Get remaining days
        remaining_days = int(response['remaining_days'])

        # Notification about remaining days is necessary or not
        key = 'trial_expire_notification_threshold'
        response = api.get(cls._THRESHOLD_API_URL, {'field': key})
        threshold = int(response[key])
        Logger.debug('Notification threshold days are {}.'.format(threshold))

        notification_required = remaining_days <= threshold

        license = License(
            trial_licensed=True,
            remaining_days=remaining_days,
            notification_required=notification_required,
        )
        return license
