# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from .subscriber import Subscriber
from ..webapi import WebApi
from ..debug import Logger


class EventStreamSubscriber(Subscriber):
    """This class subscribes to events using event stream.
    This subscriber is assumed to use in background app.
    """

    _API_URL = '/subscription/eventstream/{}'

    def __init__(self):
        """Initializes a new instance."""
        self._handlers = []

    @property
    def handlers(self):
        """Gets event handlers."""
        return self._handlers

    def _subscribe(self, api_token, event_class, event_names=None):
        """Subscribes to events using event stream."""
        api = WebApi(api_token)
        api.post(self._API_URL.format(event_class), {
            'event_names': [] if event_names is None else event_names,
        })

        Logger.info('Event for "{}" is subscribed using event stream.'.format(event_class))

    def subscribe(self, handler):
        """Subscribes to events using given event handler."""
        # Subscribe to events
        self._subscribe(handler.api_token, handler.event_class, handler.event_names)

        # Add handler
        self._handlers.append(handler)
        Logger.warn('Stream event handler for "{}" is added (existing handlers: {}).'.format(handler.event_class, len(self._handlers)))

    def unsubscribe(self, handler):
        """Unsubscribes to events."""
        if handler in self._handlers:
            self._handlers.remove(handler)
            Logger.warn('Stream event handler for "{}" is removed.'.format(handler.event_class))
        else:
            Logger.warn('Strteam handler for "{}" is not present.'.format(handler.event_class))
