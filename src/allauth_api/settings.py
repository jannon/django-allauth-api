"""
Settings for allauth API are all namespaced in the ALLAUTH_API setting.
For example your project's `settings.py` file might look like this:

ALLAUTH_API = {
    'DEFAULT_DRF_LOGIN_TYPE': 'oauth2',

    'DEFAULT_DRF_LOGIN_CLASSES': {
        'oauth2': 'allauth_api.account.api.rest_framework.authentication.OAuth2Login',
        'token': 'allauth_api.account.api.rest_framework.authentication.TokenLogin',
    }
}

This module provides the `allauth_api_setting` object, that is used to access
allauth API settings, checking for user settings first, then falling
back to the defaults.
"""
from __future__ import unicode_literals
from django.conf import settings
from django.utils import importlib, six

USER_SETTINGS = getattr(settings, 'ALLAUTH_API', None)

DEFAULTS = {
    'API_FRAMEWORK': 'rest_framework',
    'PROVIDER_PARAMETER_NAME': 'provider',
    'PROVIDER_MODULES': [
        'allauth_api.socialaccount.providers.facebook'
    ],
    'DRF_LOGIN_TYPE': 'oauth2',
    'DRF_LOGIN_CLASSES': {
        'basic': 'allauth_api.account.rest_framework.authentication.BasicLogin',
        'session': 'allauth_api.account.rest_framework.authentication.BasicLogin',
        'token': 'allauth_api.account.rest_framework.authentication.TokenLogin',
        'oauth2': 'allauth_api.account.rest_framework.authentication.OAuth2Login',
        'social_basic': 'allauth_api.socialaccount.rest_framework.authentication.BasicLogin',
        'social_session': 'allauth_api.socialaccount.rest_framework.authentication.BasicLogin',
        'social_token': 'allauth_api.socialaccount.rest_framework.authentication.TokenLogin',
        'social_oauth2': 'allauth_api.socialaccount.rest_framework.authentication.OAuth2Login',
    },
    'DRF_LOGIN_VIEW_PERMISSIONS': ('rest_framework.permissions.AllowAny',),
    'DRF_LOGOUT_VIEW_PERMISSIONS': ('rest_framework.permissions.IsAuthenticated',),
    'DRF_REGISTER_VIEW_PERMISSIONS': ('rest_framework.permissions.AllowAny',),
    'DRF_PASSWORD_VIEW_PERMISSIONS': ('rest_framework.permissions.IsAuthenticated',),
    'DRF_REGISTRATIONS_VIEW_PERMISSIONS': ('rest_framework.permissions.AllowAny',),
    'DRF_PROVIDERS_VIEW_PERMISSIONS': ('rest_framework.permissions.AllowAny',),
    'DRF_API_VIEW': 'rest_framework.views.APIView'
}


# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    'DRF_LOGIN_CLASSES',
    'DRF_LOGIN_VIEW_PERMISSIONS',
    'DRF_LOGOUT_VIEW_PERMISSIONS',
    'DRF_REGISTER_VIEW_PERMISSIONS',
    'DRF_PASSWORD_VIEW_PERMISSIONS',
    'DRF_REGISTRATIONS_VIEW_PERMISSIONS',
    'DRF_PROVIDERS_VIEW_PERMISSIONS',
    'DRF_API_VIEW',
)


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if isinstance(val, six.string_types):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    elif isinstance(val, dict):
        new_val = {}
        for k, v in val.items():
            new_val[k] = import_from_string(v, setting_name)
        val = new_val
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        # Nod to tastypie's use of importlib.
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        msg = "Could not import '%s' for API setting '%s'. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class AllAuthAPISettings(object):
    """
    A settings object, that allows API settings to be accessed as properties.
    For example:

        from allauth_api.settings import allauth_api_settings
        print allauth_api_settings.DRF_LOGIN_TYPE

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        self.user_settings = user_settings or {}
        self.defaults = defaults or {}
        self.import_strings = import_strings or ()

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if val and attr in self.import_strings:
            val = perform_import(val, attr)

        self.validate_setting(attr, val)

        # Cache the result
        setattr(self, attr, val)
        return val

    def validate_setting(self, attr, val):
        if attr == 'FILTER_BACKEND' and val is not None:
            # Make sure we can initialize the class
            val()

allauth_api_settings = AllAuthAPISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
