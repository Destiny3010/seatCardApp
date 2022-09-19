# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from mfplib.events import webhook


def configure(config):
    """Configures routes."""
    # Set Webhook URL
    webhook_url = '/webhooks'
    webhook.set_url(webhook_url)
    config.add_route('webhooks', webhook_url, xhr=False)

    # Set service routes (route name, URL)
    routes = [
        ('print_jobs', '/print/jobs'),
        ('license_verify', 'app/license/verify'),
        ('license_remove', 'app/license/remove'),
        ('license_status', 'app/license/status'),
        ('mfpdevice_capability', 'mfpdevice/capability'),
        ('app_context', 'app/context/self'),
    ]

    # Register routes
    for name, url in routes:
        config.add_route(name, url, xhr=True)
