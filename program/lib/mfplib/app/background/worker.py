# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

import traceback
from threading import Thread, Event
from queue import Queue

from .queue_entry import QueueEntry
from ...debug import Logger


class Worker(Thread):
    """This class consumes a task in queue."""

    def __init__(self, worker_id, queue):
        super().__init__(daemon=True)
        self._worker_id = worker_id
        self._queue = queue

        self._running_task_entry = None
        self._terminated = False

    @property
    def running_task_entry(self):
        return self._running_task_entry

    def run(self):
        """Executes tasks in queue."""
        Logger.info('Worker {} is started.'.format(self._worker_id))

        while True:
            # Retrieve task from queue and execute
            entry = self._queue.get(block=True)
            task = entry.task
            payload = entry.payload
            self._running_task_entry = entry

            self._execute_task(task, payload)
            self._queue.task_done()

            # Abort thread if worker is terminated
            if self._terminated:
                break

            # Release session
            entry.unlock_session()
            self._running_task_entry = None

        Logger.info('Worker {} is terminated.'.format(self._worker_id))

    def _execute_task(self, task, payload=None):
        """Executes a task."""
        try:
            Logger.warn('Worker {} tries to execute a task.'.format(self._worker_id))

            if payload is None:
                task.execute()
            else:
                task.execute(payload)

            Logger.warn('Task is done by worker {}.'.format(self._worker_id))
        except Exception as e:
            Logger.error(traceback.format_exc())
            self._invoke_on_error(task, e)

    def _invoke_on_error(self, task, error):
        """Invokes on_error method for task."""
        try:
            task.on_error(error)
        except Exception:
            Logger.error(traceback.format_exc())

    def terminate(self):
        """Terminates running worker."""
        self._terminated = True


class WorkerHost(Thread):
    """This class hosts worker threads."""

    _current = None

    def __init__(self, worker_count):
        super().__init__(daemon=False)
        self._terminate_event = Event()
        self._queue = Queue()
        self._workers = []

        self._worker_count = worker_count

    @property
    def worker_count(self):
        """Gets worker count."""
        return self._worker_count

    def start(self):
        """Starts this thread."""
        WorkerHost._current = self
        super().start()

    def run(self):
        """Executes worker hosting on thread."""
        try:
            Logger.info('Worker host thread is started.')

            # Start worker threads
            for counter in range(self._worker_count):
                worker = Worker(counter + 1, self._queue)
                self._workers.append(worker)
                worker.start()

            # Wait for app terminated
            self._terminate_event.wait()
            Logger.info('Worker host thread is terminated.')
        except Exception:
            Logger.error(traceback.format_exc())

    def terminate(self):
        """Terminates worker hosting thread."""
        # Terminate all workers
        for worker in self._workers:
            worker.terminate()

        # Abort running or waiting tasks
        self._abort_tasks()

        # Kill running thread
        self._terminate_event.set()

    def _abort_tasks(self):
        """Abort running or waiting tasks."""
        # Get running task entries
        entries = [
            worker.running_task_entry
            for worker in self._workers if worker.running_task_entry
        ]

        # Get waiting task entries
        while not self._queue.empty():
            entries.append(self._queue.get())

        # Sort by start timestamp
        entries = sorted(entries, key=lambda x: x.task.dispatched_at)

        Logger.warn('{} tasks are not completed at background app stopped.'.format(len(entries)))

        # Abort task
        for entry in entries:
            self._invoke_on_aborted(entry.task)
            entry.unlock_session()

    def _invoke_on_aborted(self, task):
        """Invokes on_aborted method for task."""
        try:
            task.on_aborted()
        except Exception:
            Logger.error(traceback.format_exc())

    @classmethod
    def enqueue_task(cls, task, payload=None):
        """Puts a task into queue."""
        host = cls._current

        if host is None:
            raise RuntimeError('Worker host thread is not started.')

        # Invoke hook method
        task.on_enqueued(payload)

        # Create queue entry
        entry = QueueEntry(task, payload)

        # Lock app session
        entry.lock_session(task.api_token)

        # Enqueue
        host._queue.put(entry)
