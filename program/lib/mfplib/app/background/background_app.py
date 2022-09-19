# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

import traceback

from .comm_server import CommunicationServer
from .worker import WorkerHost

from ...jobs.image import ImageSourceRepository
from ...events.stream import EventStreamSubscriber as Subscriber
from ...debug import Logger, LoggerType


class BackgroundApp:
    """This class is background app base."""

    def __init__(self, headers, worker_count=10):
        """Initializes a new instance.

        Args:
            headers (dict): Key value settings which are provided by app framework.
            worker_count (int): Background worker count. Default is 10.
        """
        self._api_token = headers['X-WebAPI-AccessToken']

        # Setup logger
        Logger.set_logger_type(LoggerType.BackgroundAppLogger)

        # Initialize worker host and communication server
        self._worker_host = WorkerHost(worker_count)
        self._comm_server = CommunicationServer(self._api_token)

        # Setup event subscriber
        self._subscriber = Subscriber()
        Subscriber.set_subscriber(self._subscriber)

    @property
    def api_token(self):
        """Gets API access token."""
        return self._api_token

    def on_started(self):
        """This method is invoked at background app started."""
        pass

    def on_stopped(self):
        """This method is invoked at background app stopped."""
        pass

    def onStart(self):
        try:
            Logger.warn('Background app is started.')

            # Keep image processing files
            repository = ImageSourceRepository(self._api_token)
            repository.switch_keep_mode(enabled=True)

            # Start worker host
            self._worker_host.start()

            # Open app communication
            self._comm_server.open()

            self.on_started()
        except Exception:
            Logger.error(traceback.format_exc())

    def onStop(self):
        try:
            Logger.info('Background app is stopped.')

            # Close app communication
            self._comm_server.close()

            # Terminate worker host
            self._worker_host.terminate()

            self.on_stopped()
        except Exception:
            Logger.error(traceback.format_exc())

    def onEvent(self, strEvent):
        Logger.debug('App job event occurs.')
        try:
            self._subscriber.handle_event(strEvent)
        except Exception:
            Logger.error(traceback.format_exc())

    def onConnectionOpened(self, accessToken, onConnectedEventObject):
        Logger.debug('App communication is opened from client side.')

    def onRequested(self, accessToken, onRequestedEventObject):
        try:
            Logger.debug('App communication is requested from client side.')

            # Handle request from client side
            request = onRequestedEventObject['app_server_request']['data']
            return self._comm_server.handle_requested_data(request, accessToken)
        except Exception:
            Logger.error(traceback.format_exc())

    def onConnectionClosed(self, accessToken, onClosedEventObject):
        Logger.debug('App communication is closed from client side.')
