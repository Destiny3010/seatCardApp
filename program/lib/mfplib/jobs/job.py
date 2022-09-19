# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from ..events import subscriber
from ..events.handler import EventHandler
from ..webapi import WebApi
from ..debug import Logger


class Job:
    """This class represents an MFP job.

    Attributes:
        api_token (str): API access token.
        id (int): Job ID.
    """

    def __init__(self, api_token, id):
        """Initializes a new instance."""
        self._api_token = api_token
        self._id = id

    @property
    def api_token(self):
        """Gets API access token."""
        return self._api_token

    @property
    def id(self):
        """Gets job ID."""
        return self._id

    @classmethod
    def start(cls, api_token, api_url, parameter=None, listener=None):
        """Starts a new job.

        Args:
            api_token (str): API access token.
            api_url (str): API URL to start a new job.
            parameter (dict): Request parameter.
            listener (JobListener): Job listener to handle job events.
        Returns:
            int: job ID.
        Raises:
            WebApiError: Failed to call job start API.
        """
        # Subscribe to job events
        handler = None
        if listener:
            handler = JobEventHandler(api_token, listener)
            subscriber.subscribe(handler)

        # Start a new job
        api = WebApi(api_token)
        response = api.post(api_url, parameter)

        job_id = response['WFID']
        Logger.info('New job is started by ID {}.'.format(job_id))

        # Set job ID in handler to handle job events
        if handler:
            handler.set_job_id(job_id)

        return job_id


class JobEvent(dict):
    """This class represents a job event.

    Attributes:
        api_token (str): API access token.
        name (str): Event name.
        job_id (int): Job ID.
        status (str): Job status.
        reason (str): Job status reason.
    """

    def __init__(self, event):
        """Initializes a new instance."""
        super().__init__(event)

        self.api_token = event.get('accesstoken', None)
        self.name = event.get('event_name', None)

        job_status = event.get('job_status', None)
        if job_status:
            self.job_id = job_status.get('job_id', None)
            self.status = job_status.get('status', None)
            self.reason = job_status.get('status_reason', None)
        else:
            self.job_id = None
            self.status = None
            self.reason = None


class JobListener:
    """This class handles job events."""

    def handle_event(self, event):
        """Handles job event.

        Args:
            job (Job): Job.
            event (JobEvent): Job event.
        """
        raise NotImplementedError()


class JobEventHandler(EventHandler):
    """This class handles job events."""

    _EVENT_CLASS = 'jobs'

    def __init__(self, api_token, listener):
        """Initializes a new instance.

        Args:
            api_token (str): API access token.
            listener (JobListener): Job listener.
        """
        super().__init__(api_token, self._EVENT_CLASS, event_names=[])
        self._listener = listener
        self._job_id = None

    @property
    def listener(self):
        """Gets job listener."""
        return self._listener

    @property
    def job_id(self):
        """Gets related job ID."""
        return self._job_id

    def set_job_id(self, job_id):
        """Sets job ID."""
        self._job_id = job_id

    def handle_event(self, event):
        """Handles a job event.

        Args:
            event (dict): Job event data.
        """
        parsed_event = JobEvent(event)
        if parsed_event.job_id is None or parsed_event.job_id != self._job_id:
            # Received job event is not target for this handler
            return

        # Invoke job listener
        try:
            self._listener.handle_event(parsed_event)
            Logger.info('Job event (for ID: {}) has been handled by job listener "{}".'.format(parsed_event.job_id, type(self._listener).__name__))
        finally:
            # Delete event handler if job is completed
            if parsed_event.name == 'jobs_completed':
                subscriber.unsubscribe(self)
