# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from collections import namedtuple
from ..webapi import WebApi


class ProxyConfig(namedtuple('ProxyConfig', ('url', 'exceptional_hosts'))):
    """This class represents a network proxies setting.

    Attributes:
        url (str): Proxy server URL for HTTP/HTTPS network access.
        exceptional_hosts (list[str]): Host names which are excepted to use proxies.
    """
    @property
    def configured(self):
        """Gets network proxies are configured or not."""
        return len(self.url) > 0


class Network:
    """This class manages device network."""

    _PROXIES_API_URL = '/setting/network/proxies'

    _CERT_FILE_PATH = '/application/common/security/ca_cert_chain'

    _DELIMETER = ';'

    def __init__(self, api_token):
        """Initializes a new instance."""
        self._api = WebApi(api_token)

    @classmethod
    def get_certificate_path(cls):
        """Gets certificate file path for SSL/TLS communication.

        Returns:
            str: Certificate file path.
        """
        return cls._CERT_FILE_PATH

    def get_proxies(self):
        """Gets proxy settings.

        Returns:
            ProxyConfig: Proxy settings.
        """
        # Get setting
        response = self._api.get(self._PROXIES_API_URL)

        # Build proxy server URL
        host = response['host_name']
        port = response['port_number']
        proxy_url = 'http://{}:{}/'.format(host, port) if host else ''

        # Parse exceptional hosts
        exceptional_hosts = [
            host
            for host in response['exceptional_url'].split(self._DELIMETER)
            if len(host) > 0
        ]

        return ProxyConfig(proxy_url, exceptional_hosts)
