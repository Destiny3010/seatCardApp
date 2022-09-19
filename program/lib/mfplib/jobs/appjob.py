# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from threading import Event

from .job import JobListener
from .errors import JobTimeoutError
from ..debug import Logger


class AppJobListener(JobListener):
    """This class handles app job events."""

    _DEFAULT_TIMEOUT = 90 * 60  # 90 min

    def __init__(self):
        """Initializes a new instance."""
        self._listener = Event()
        self._event = None

    def listen(self, timeout=None):
        """Listens to app job event at completed.

        Args:
            timeout (int): Listening timeout (seconds).
                If None is passed, default timeout (90 minutes) is used.
        Returns:
            JobEvent: Job event.
        Raises:
            JobTimeoutError: Job is not completed in timeout.
        """
        timeout = self._DEFAULT_TIMEOUT if timeout is None else timeout

        # Wait for job event
        completed = self._listener.wait(timeout)
        if not completed:
            raise JobTimeoutError()

        # Return job event
        return self._event

    def handle_event(self, event):
        """Handles an app job event.

        Args:
            event (JobEvent): Job event.
        """
        Logger.warn('App job event is received (job ID: {}, name: {}, status: {}, reason: {}).'.format(event.job_id, event.name, event.status, event.reason))

        if event.name == 'jobs_completed':
            # Notify job completed
            self._event = event
            self._listener.set()
