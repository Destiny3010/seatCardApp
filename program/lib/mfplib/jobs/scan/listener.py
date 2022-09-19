# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from collections import namedtuple
from enum import Enum

from . import job
from ..job import JobListener
from ...events import sse
from ...app.lock import HomeAppLock
from ...app.comm.client import CommunicationError
from ...app.comm.dispatcher import Dispatcher
from ...debug import Logger


class EventType(Enum):
    """This enum represents a scan event type."""
    PageScanned = 'page_scanned'
    PreviewCreated = 'preview_created'
    Suspended = 'suspended'
    FilingStarted = 'filing_started'
    Canceled = 'canceled'
    Completed = 'completed'
    Failed = 'failed'


class ScanJobFailedError(Exception):
    """This class represents that scan job is not completed successfully."""

    def __init__(self, reason, message=None):
        """Initializes a new instance.

        Args:
            reason (str): Reason of scan job failure.
            message (str): Error message.
        """
        super().__init__(message or 'Scan job is not completed successfully.')
        self.reason = reason


class ScanJobResult(namedtuple('ScanJobResult', (
        'api_token', 'id', 'scanned_pages', 'omitted_pages'))):
    """This class represents a scan job result.

    Attributes:
        api_token (str): API access token.
        id (int) Scan job ID.
        scanned_pages (int): Scanned page count.
        omitted_pages (int): Omitted page count such as blank.
    """
    pass


class EventNotifier(namedtuple('EventNotifier', ('api_token', 'job_id'))):
    """This class notifies scan job events to client side using SSE."""

    def notify(self, event_name, body=None):
        """Notifies a scan job event.

        Args:
            event_name (str): Event name.
            body (dict): Event body.
        """
        body_ = {'job_id': self.job_id}
        if body:
            body_.update(body)

        sse.send_event(
            api_token=self.api_token,
            type=ScanJobListener._JOB_TYPE,
            name=event_name,
            body=body_,
        )


class ScanJobListener(JobListener):
    """This class handles a scan job event."""

    _JOB_TYPE = 'scan_job'

    _SUSPENDED_REASONS = {
        'wait_next_original': 'wait_next',  # Suspended for next sheet
        'user_request': 'wait_next',  # Stopped while DF scanning by user operation
        'max_page': 'max_page',  # Suspended because of scan pages reached to max
        'job_status_reason_adf_jam': 'df_jam',  # DF jam
        'cover_open': 'cover_open',  # Cover open
    }

    _FAILED_REASONS = {
        'job_status_reason_adf_jam': 'not_started',  # DF jam occurs at first page
        'cover_open': 'not_started',  # Cover open occurs at first page
        'hard_disk_full': 'storage_full',  # Storage full
        'wait_next_original': 'not_started',  # Original is missed on DF before scan started
        'all_pages_omitted': 'all_omitted',  # All pages are omitted because of blank
        'copy_protection': 'copy_protection',  # Job is rejected by copy protection
        'counterfeit_money': 'counterfeit_prohibited',  # Job is rejected by counterfeit
    }

    def __init__(self):
        """Initializes a new instance."""
        super().__init__()
        self._lock = None

        # Cache job failed reason at input processing completed
        # Because status reason of job completed event is not stable
        # (in some cases, status reason is 'fatal_error' instead of 'copy_protection' etc)
        self._cached_reason = None

    def handle_event(self, event):
        """Handles a scan event.

        Args:
            event (JobEvent): Scan job event.
        """
        handler = {
            'jobs_page_scanned': self._handle_page_scanned,
            'jobs_preview_img_created': self._handle_preview_created,
            'jobs_input_processing_suspended': self._handle_input_processing_suspended,
            'jobs_suspended': self._handle_job_suspended,
            'jobs_input_processing_completed': self._handle_input_processesing_completed,
            'jobs_completed': self._handle_job_completed,
        }.get(event.name, None)

        if handler:
            notifier = EventNotifier(event.api_token, event.job_id)
            handler(event, notifier)
        else:
            # Unexpected event
            Logger.warn('Unexpected scan event "{}" occurs.'.format(event.name))

    def _handle_page_scanned(self, event, notifier):
        """Handles a page scanned event."""
        page_number = event['page_num']
        Logger.warn('Page scanned event (page: {}) occurs.'.format(page_number))

        # Send event to client
        notifier.notify(EventType.PageScanned.value, {'page_number': page_number})

    def _handle_preview_created(self, event, notifier):
        """Handles a preview image created event."""
        page_number = event['page_num']
        preview_url = event['preview_url']
        Logger.warn('Preview image created event (page: {}) occurs.'.format(page_number))

        # Send event to client
        notifier.notify(EventType.PreviewCreated.value, {
            'page_number': page_number,
            'preview_url': preview_url,
        })

    def _handle_input_processing_suspended(self, event, notifier):
        """Handles an input processing suspended event."""
        Logger.warn('Scan job input processing suspended event is received (reason: {}).'.format(event.reason))

    def _handle_job_suspended(self, event, notifier):
        """Handles a job suspended event."""
        Logger.warn('Scan job suspended event is received (reason: {}).'.format(event.reason))

        # Map event reason to app reason value
        suspended_reason = self._SUSPENDED_REASONS.get(event.reason, 'unexpected')
        Logger.warn('Scan job is suspended by reason "{}".'.format(suspended_reason))

        # Send event to client
        notifier.notify(EventType.Suspended.value, {'reason': suspended_reason})

    def _handle_input_processesing_completed(self, event, notifier):
        """Handles an input processing completed event."""
        Logger.warn('Scan job input processing completed event is received (status: {}, reason: {}).'.format(event.status, event.reason))

        # Lock home app session if successful case
        if event.reason == 'success':
            self._lock = HomeAppLock(event.api_token)
            self._lock.acquire()

            # Send event to client
            notifier.notify(EventType.FilingStarted.value)
        else:
            # Cache failed reason for job completed event
            self._cached_reason = event.reason

    def _handle_job_completed(self, event, notifier):
        """Handles a job completed event."""
        Logger.warn('Scan job completed event is received (status: {}, reason: {}).'.format(event.status, event.reason))

        # Get scan result
        result = self._get_result(event)

        try:
            if event.status != 'completed':
                Logger.warn('Job is completed incorrectly because of status "{}".'.format(event.status))
                raise ScanJobFailedError(reason='unexpected')

            # Specify completed reason
            if event.reason == 'success':
                # Job is completed successfully
                Logger.warn('Scan job is completed successfully.')
                self.on_completed(result)

                self._notify_completed(notifier, result)
            elif event.reason == 'user_request':
                # Job is deleted by user operation or deleted from TopAccess
                Logger.warn('Scan job is canceled by user request.')
                notifier.notify(EventType.Canceled.value)
            else:
                # Use cached job status reason
                reason = self._cached_reason

                # Map event reason to app reason value
                failed_reason = self._FAILED_REASONS.get(reason, 'unexpected')
                Logger.warn('Scan job is failed by reason "{}".'.format(failed_reason))

                raise ScanJobFailedError(reason=failed_reason)
        except ScanJobFailedError as e:
            Logger.warn('Scan job is not completed successfully (reason: {}).'.format(e.reason))
            self._notify_failed(notifier, result, failed_reason=e.reason or 'unexpected')
        except Exception as e:
            Logger.error('Unexpected error occurs in handling scan job completed event (error type: {}).'.format(type(e).__name__))
            self._notify_failed(notifier, result, failed_reason='unexpected')
        finally:
            self._cached_reason = None
            job.ScanJob._running_job = None

            # Unlock home app session
            if self._lock is not None:
                self._lock.release()
                self._lock = None

    def _get_result(self, event):
        scanned_result = event.get('page_scanned_result', None)

        scanned_pages, omitted_pages = (0, 0) if scanned_result is None else (
            scanned_result.get('total_pages', 0),
            scanned_result.get('omitted_blank_pages', 0),
        )

        result = ScanJobResult(
            api_token=event.api_token,
            id=event.job_id,
            scanned_pages=scanned_pages,
            omitted_pages=omitted_pages,
        )
        return result

    def _notify_completed(self, notifier, result):
        """Notifies a scan job completed event to client side."""
        notifier.notify(EventType.Completed.value, {
            'scanned_pages': result.scanned_pages,
            'omitted_pages': result.omitted_pages,
        })

    def _notify_failed(self, notifier, result, failed_reason):
        """Notifies a scan job failed event to client side."""
        notifier.notify(EventType.Failed.value, {
            'scanned_pages': result.scanned_pages,
            'omitted_pages': result.omitted_pages,
            'reason': failed_reason,
        })

    def on_completed(self, result):
        """This method is invoked when scan job is completed successfully.
            After this method is finished, scan job completed event is notified to client side.

        Args:
            result (ScanJobResult): Scan job result.
        Note:
            If you need to notify failure event (for example, background task dispatch failed),
            raise ScanJobFailureError.
        """
        pass

    @classmethod
    def create(cls, task_class, payload):
        """Creates a scan job listener which dispatches a task to execute in background app.

        Args:
            task_class (str): Task class path (e.g. tasks.upload.UploadTask).
                Task class must be implemented under 'lib' or 'backgroundapp' directory.
            payload (TaskPayload): Task payload.
                If payload class is inherited from TaskPayload class,
                the super class must be implemented under 'lib' directory.
        Note:
            You can create a listener with task payload: ::

                payload = TaskPayload(document_name='Sample')
                ScanJobListener.create('tasks.upload.UploadTask', payload)

            When the task is launched in background app, you can access the payload: ::

                class UploadTask(Task):
                    def execute(self, payload):
                        document_name = payload.document_name

            If failed to dispatch a task by communication error,
            failed event will be notified via SSE where the failed reason is ``'communication_failed'``.
        """
        return TaskDispatchingScanJobListener(task_class, payload)


class TaskDispatchingScanJobListener(ScanJobListener):
    """This class dispatching a task after scan job completed."""

    _FAILED_REASON = 'communication_failed'

    def __init__(self, task_class, payload):
        """Initializes a new instance.

        Args:
            task_class (str): Task class path.
            payload (TaskPayload): Payload of task which is running in background.
        """
        super().__init__()
        self._task_class = task_class
        self._payload = payload

    @property
    def task_class(self):
        return self._task_class

    @property
    def payload(self):
        return self._payload

    def on_completed(self, result):
        """Handles scan job completed event.

        Args:
            result (ScanJobResult): Scan job result.
        """
        try:
            dispatcher = Dispatcher(result.api_token)
            dispatcher.dispatch(task_class=self._task_class, payload=self._payload)

            Logger.warn('Scan task is dispatched successfully.')
        except CommunicationError:
            Logger.error('Scan task cannot be dispatched because of communication error.')
            raise ScanJobFailedError(reason=self._FAILED_REASON)
