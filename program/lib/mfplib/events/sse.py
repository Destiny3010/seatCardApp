# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

import importlib

_sse_client = None


def send_event(api_token, type, name, body=None):
    """Sends an event to client side via SSE.

    Args:
        api_token (str): API access token.
        type (str): Event type.
        name (str): Event name.
        body (dict): Event body.
    """
    global _sse_client

    if _sse_client is None:
        # Import SSE client dynamically
        # (in order to perform unit testing without SSE client importing)
        module_name = 'hmserver.apps.common.eventmanagement.eventhandler'
        module = importlib.import_module(module_name)
        _sse_client = module.EventHandler()

    _sse_client.sendNotification(api_token, {
        'type': type,
        'name': name,
        'body': {} if body is None else body,
    })
