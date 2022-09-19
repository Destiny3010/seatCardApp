# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from pyramid.view import view_config

from mfplib.events import webhook

from .view import View


class WebhookView(View):
    """This class handles a webhook event request."""

    @view_config(route_name='webhooks', request_method='POST')
    def handle(self):
        """Handles a webhook event request."""
        event = self.request.json_body
        webhook.handle_event(event)

        return self.response.ok()
