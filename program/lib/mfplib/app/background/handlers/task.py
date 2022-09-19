# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from .handler import RequestHandler
from ..worker import WorkerHost


class TaskHandler(RequestHandler):
    """This class handles a task request."""

    def handle_request(self, request):
        """Handles a task request."""
        task = request['task']

        # Set attributes
        task._set_task_attributes(
            api_token=self.api_token,
            dispatched_at=request['dispatched_at'],
            locale=request['locale'],
        )

        # Put task into queue
        WorkerHost.enqueue_task(task)
