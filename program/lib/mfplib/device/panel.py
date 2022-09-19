# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from enum import Enum

from ..webapi import WebApi
from ..debug import Logger


class LedType(Enum):
    """This enum represents an LED type."""
    StartKey = 'start_key'
    ResetKey = 'reset_key'


class PanelScreen(Enum):
    """This enum represents a screen type of panel."""
    Default = 'default'
    Home = 'home'
    JobStatus = 'job_status'


class Panel:
    """This class manages a device panel."""

    _SCREEN_API_URL = '/mfpdevice/panel/action/transfers'
    _LED_API_URL = '/mfpdevice/panel/leds/{}'

    _LED_KEYS = {
        LedType.StartKey: 'start_button',
        LedType.ResetKey: 'fc_button',
    }

    def __init__(self, api_token):
        """Initializes a new instance.

        Args:
            api_token (str): API access token.
        """
        self._api = WebApi(api_token)

    def switch_led(self, led_type, turned_on=False):
        """Switches LED status.

        Args:
            led_type (LedType): Target LED type.
            turned_on (bool): Turned on LED or not.
        """
        # Specify LED type
        key = self._LED_KEYS.get(led_type, None)
        if key is None:
            return

        # Switch LED state
        status = 'on' if turned_on else 'off'
        self._api.patch(self._LED_API_URL.format(key), {'led_status': status})
        Logger.debug('LED {0} status is switched to {1}.'.format(led_type.name, status))

    def blink_led(self, led_type, interval=1000):
        """Turns on LED with blink.

        Args:
            led_type (LedType): Target LED type.
            interval (int): Blink interval by milli-seconds.
        """
        # Specify LED type
        key = self._LED_KEYS.get(led_type, None)
        if key is None:
            return

        # Turn on with blink
        self._api.patch(self._LED_API_URL.format(key), {
            'led_status': 'blink',
            'interval': interval,
        })
        Logger.debug('LED {0} is turned on with blink (interval: {1}).'.format(led_type.name, interval))

    def transit(self, screen):
        """Transits to a panel screen.

        Args:
            screen (PanelScreen): Panel screen.
        """
        self._api.post(self._SCREEN_API_URL, {'screen': screen.value})
        Logger.debug('Panel screen transits to {}.'.format(screen.name))
