# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from ..debug import Logger


class Subscriber:
    """This class subscribes to events from MFP."""

    _subscriber = None

    @classmethod
    def get_subscriber(cls):
        """Gets current subscriber.
        If specific subscriber is not configured, None will be returned.

        Returns:
            Subscriber: Current subscriber.
        """
        return cls._subscriber

    @classmethod
    def set_subscriber(cls, subscriber):
        """Sets subscriber to handle events.

        Args:
            Subscriber: Subscriber to handle events.
        """
        Subscriber._subscriber = subscriber
        Logger.warn('Subscriber "{}" is assigned.'.format(type(subscriber).__name__))

    @property
    def handlers(self):
        """Gets event handlers."""
        raise NotImplementedError()

    def subscribe(self, handler):
        """Subscribes to events using given event handler.

        Args:
            handler (EventHandler): Event handler.
        """
        raise NotImplementedError()

    def unsubscribe(self, handler):
        """Unsubscribes to events.

        Args:
            handler (EventHandler): Existing event handler.
        """
        raise NotImplementedError()

    def _get_handlers(self, api_token, event_class):
        """Gets existing event handlers.

        Args:
            api_token (str): API access token.
            event_class (str): Event class.
        Returns:
            list[EventHandler]: Event handlers.
        """
        handlers = [
            handler
            for handler in self.handlers
            if handler.api_token == api_token and handler.event_class == event_class
        ]
        return handlers

    def handle_event(self, event):
        """Handles a received event using event handlers.

        Args:
            event (dict): Received event data.
        """
        # Parse event class name
        event_class = event.get('event_class', None)
        if event_class is None:
            Logger.warn('Event class is not described in received event information.')
            return

        # Parse API token
        api_token = event.get('accesstoken', None)
        if api_token is None:
            Logger.warn('Received event "{}" does not have API access token.'.format(event_class))
            return

        Logger.warn('Event "{}" is received.'.format(event_class))

        # Distributes event to handlers
        handlers = self._get_handlers(api_token, event_class)

        if not handlers:
            Logger.warn('No handler is present to handle an event "{}".'.format(event_class))
            return

        for handler in handlers:
            handler.handle_event(event)

        Logger.warn('Received event "{}" has been handled.'.format(event_class))


def subscribe(handler):
    """Subscribes to events using given event handler.

    Args:
        handler (EventHandler): Event handler.
    """
    subscriber = Subscriber.get_subscriber()
    if subscriber is None:
        raise RuntimeError('Specific event subscriber is not configured.')

    subscriber.subscribe(handler)


def unsubscribe(handler):
    """Unsubscribes to events.

    Args:
        handler (EventHandler): Existing event handler.
    """
    subscriber = Subscriber.get_subscriber()
    if subscriber is None:
        raise RuntimeError('Specific event subscriber is not configured.')

    subscriber.unsubscribe(handler)
