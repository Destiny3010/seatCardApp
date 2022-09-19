# Copyright(c) 2020 Toshiba Tec Corporation, All Rights Reserved.

from collections import namedtuple
from enum import Enum

from ..webapi import WebApi
from ..debug import Logger


class PermissionType(Enum):
    """This enum represents a user permission type."""
    StoreToLocal = 'store_to_local'
    StoreToRemote = 'store_to_remote'
    Print = 'print'

    @classmethod
    def _parse(cls, api_value):
        permission_type = {
            'remote_store_job': cls.StoreToRemote,
            'local_store_job': cls.StoreToLocal,
            'print_job': cls.Print,
        }.get(api_value, None)

        return permission_type


class LoginUser(namedtuple('LoginUser', ('id', 'name', 'domain', 'permissions'))):
    """This class represents a current login user.

    Attributes:
        id (int): Login user ID.
        name (str): Login user name.
        domain (str): Login user domain name.
        permissions (list[PermissionType]): Login user permissions.
    """

    _SESSION_API_URL = '/session/current'

    @classmethod
    def get_current(cls, api_token):
        """Gets a current login user.

        Args:
            api_token (str): API access token.
        Returns:
            User: Current login user. If user authentication is disabled, None will be returned.
        """
        # Get current user
        api = WebApi(api_token)
        response = api.get(cls._SESSION_API_URL)
        response_user = response.get('login_user', {})

        if len(response_user) == 0:
            # User authentication is disabled
            Logger.debug('No user is authenticated.')
            return None

        # Get current login user
        domain = '' if response_user['auth_method'] == 'local' else response_user['auth_server_name']
        user = cls(
            id=response_user['id'],
            name=response_user['name'],
            domain=domain,
            permissions=cls._parse_permissions(response_user['permission_list']),
        )

        Logger.debug('Authenticated user (ID: {}) is retrieved.'.format(user.id))
        return user

    @classmethod
    def _parse_permissions(cls, permission_list):
        permissions = [
            PermissionType._parse(value)
            for value in permission_list
        ]

        return list(filter(lambda x: x is not None, permissions))
