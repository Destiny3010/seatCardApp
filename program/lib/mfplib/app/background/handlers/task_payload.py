# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

import importlib

from .handler import RequestHandler
from ..worker import WorkerHost

from mfplib.debug import Logger


class TaskPayloadHandler(RequestHandler):
    """This class handles a task payload request."""

    def handle_request(self, request):
        """Handles a task payload request."""
        # Create task instance
        task_class = request['task_class']
        Logger.info('Task {} is requested.'.format(task_class))

        task = self._create_task(task_class)

        # Set attributes
        task._set_task_attributes(
            api_token=self.api_token,
            dispatched_at=request['dispatched_at'],
            locale=request['locale'],
        )

        # Put task into queue
        WorkerHost.enqueue_task(task, request['payload'])

    def _create_task(self, task_class):
        """Creates task instance."""
        try:
            module_path, class_name = self._parse_class_path(task_class)
            module = importlib.import_module(module_path)
            class_type = getattr(module, class_name)
        except (ImportError, AttributeError, ValueError):
            raise RuntimeError('Task class {} is not found.'.format(task_class))

        return class_type()

    def _parse_class_path(self, class_path):
        """Parses class path to module path and class name (foo.Bar -> foo, Bar)."""
        index = class_path.rindex('.')
        return (class_path[:index], class_path[index + 1:])
