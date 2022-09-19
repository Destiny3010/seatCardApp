# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from .subscriber import Subscriber
from ..webapi import WebApi
from ..debug import Logger


def set_url(url):
    """Sets webhook URL."""
    Subscriber.set_subscriber(WebhookSubscriber(url))


def handle_event(event):
    """Handles an webhook event."""
    subscriber = Subscriber.get_subscriber()

    if subscriber is None:
        raise RuntimeError('Specific event subscriber is not configured.')

    subscriber.handle_event(event)


class WebhookSubscriber(Subscriber):
    """This class subscribes to event using webhook.
    This subscriber is assumed to use in home/setting app.

    Note:
        This subscriber cannot host multi event handlers for same event class.
        For example, once a jobs event handler is registered, only scan job events are handlerable.
        Both print and scan job events cannot be handlerable.
        If print job event handler is added, the handler overwrites existing scan job event handler
        (and scan job events will not be handlerable).
    """

    _API_URL = '/subscription/webhooks/{}'

    def __init__(self, webhook_url):
        """Initializes a new instance.

        Args:
            webhook_url (str): Webhook URL to receive events.
        """
        self._webhook_url = webhook_url
        self._handlers = {}

    @property
    def webhook_url(self):
        """Gets webhook url."""
        return self._webhook_url

    @property
    def handlers(self):
        """Gets event handlers."""
        return self._handlers.values()

    def _subscribe(self, api_token, event_class, event_names=None):
        """Subscribes to events using webhook."""
        api = WebApi(api_token)
        api.post(self._API_URL.format(event_class), {
            'event_names': [] if event_names is None else event_names,
            'target_url': self._webhook_url,
        })

        Logger.info('Event for "{}" is subscribed using webhook.'.format(event_class))

    def subscribe(self, handler):
        """Subscribes to events using given event handler."""
        # Subscribe to events
        self._subscribe(handler.api_token, handler.event_class, handler.event_names)

        # Add handler
        self._handlers[handler.event_class] = handler
        Logger.warn('Webhook event handler for "{}" is added (existing handlers: {}).'.format(handler.event_class, len(self._handlers)))

    def unsubscribe(self, handler):
        """Unsubscribes to events."""
        event_class = handler.event_class

        if event_class in self._handlers:
            self._handlers.pop(event_class)
            Logger.warn('Webhook event handler for "{}" is removed.'.format(event_class))
        else:
            Logger.warn('Webhook event handler for "{}" is not present.'.format(event_class))
