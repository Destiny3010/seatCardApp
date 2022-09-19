# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.


class EventHandler:
    """This class handles to events from MFP.

    Attributes:
        api_token (str): API access token.
        event_class (str): Event class which is provided by framework.
        event_names (list[str]): Event names.
    Note:
        If event names are different inspit of same event class,
        all specified events will be received as below.
        1. event class: jobs, event names: [event_a, event_b]
        2. event class: jobs, event names: [event_c]
        -> received event for jobs: event_a, event_b, event_c

        So, for one event class, same event_names must be specified.
    """

    def __init__(self, api_token, event_class, event_names=None):
        """Initializes a new instance."""
        self._api_token = api_token
        self._event_class = event_class
        self._event_names = event_names

    @property
    def api_token(self):
        """Gets API access token."""
        return self._api_token

    @property
    def event_class(self):
        """Gets target event class."""
        return self._event_class

    @property
    def event_names(self):
        """Gets target event names."""
        return self._event_names

    def handle_event(self, event):
        """Handles an event.

        Args:
            event (dict): Event data.
        """
        raise NotImplementedError()
