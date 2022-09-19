# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from collections import namedtuple

from ..webapi import WebApi


class Version(namedtuple('Version', ('major', 'minor', 'revision', 'branch'))):
    """This class represents an app framework version.

    Attributes:
        major (int): Major version number.
        minor (int): Minor version number.
        revision (int): Revision number.
        branch (str): Branch version.
    """

    _API_URL = '/app/framework/info'

    _cache = None

    def __str__(self):
        return '{}.{}.{}{}'.format(self.major, self.minor, self.revision, self.branch)

    def __repr__(self):
        return str(self)

    def is_equal(self, major, minor, revision, branch=''):
        """Gets whether current framework version equals to given version.

        * Framework version: 3.5.2, Given version: 3.5.2, Return value: True
        * Framework version: 3.5.2, Given version: 2.1.0, Return value: False
        * Framework version: 3.5.2b, Given version: 3.5.2b, Return value: True
        * Framework version: 3.5.2, Given version: 3.5.2b, Return value: False
        * Framework version: 3.5.2b, Given version: 3.5.2, Return value: False

        Args:
            major (int): Major version number.
            minor (int): Minor version number.
            revision (int): Revision number.
            branch (str): Branch version.
        Returns:
            bool: Framework version equals to given version.
        """
        pairs = [
            (self.major, major),
            (self.minor, minor),
            (self.revision, revision),
            (self.branch, branch),
        ]
        return all([pair[0] == pair[1] for pair in pairs])

    def is_older(self, major, minor, revision):
        """Gets whether current framework version is older than given version.

        * Framework version: 3.5.2, Given version: 3.5.3, Return value: True
        * Framework version: 3.5.2, Given version: 3.5.2, Return value: False
        * Framework version: 3.5.2, Given version: 3.4.9, Return value: False
        * Framework version: 3.5.2b, Given version: 3.5.3, Return value: True
        * Framework version: 3.5.2b, Given version: 3.5.2, Return value: False

        Args:
            major (int): Major version number.
            minor (int): Minor version number.
            revision (int): Revision number.
        Returns:
            bool: Framework version is older than given version.
        """
        pairs = [
            (self.major, major),
            (self.minor, minor),
            (self.revision, revision),
        ]

        for pair in pairs:
            if pair[0] == pair[1]:
                continue
            elif pair[0] < pair[1]:
                return True
            else:
                return False

        return False

    @classmethod
    def get_current(cls, api_token):
        """Gets current framework version.

        Args:
            api_token (str): API access token.
        Returns:
            Version: Current framework version.
        """
        if cls._cache is None:
            cls._cache = cls._get_version(api_token)

        return cls._cache

    @classmethod
    def _get_version(cls, api_token):
        """Gets framework version."""
        api = WebApi(api_token)
        response = api.get(cls._API_URL)

        version = cls(
            major=response['version_major'],
            minor=response['version_minor'],
            revision=response['version_revision'],
            branch=response['version_branch'],
        )
        return version
