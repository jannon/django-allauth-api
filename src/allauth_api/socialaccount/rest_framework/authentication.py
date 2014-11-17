from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from allauth_api.account.rest_framework import authentication as account_auth
from allauth_api.settings import allauth_api_settings
from allauth_api.socialaccount.providers import registry


class SocialAuthentication(BaseAuthentication):
    """
    An authentication method that hands the duty off to the specified provider
    the settings.PROVIDER_PARAMETER_NAME must be present in the request data
    """

    def authenticate(self, request):
        provider_id = request.DATA.get(allauth_api_settings.PROVIDER_PARAMETER_NAME)

        if provider_id:
            provider = registry.by_id(provider_id)
            if provider:
                return provider.authneticate(request)
            else:
                msg = "%s %s" % (_("no provider found for"), provider_id)
                raise AuthenticationFailed(msg)
        else:
            msg = "%s %s" % (allauth_api_settings.PROVIDER_PARAMETER_NAME,
                             _("parameter must be provided"))
            raise AuthenticationFailed(msg)


class BasicLogin(account_auth.BasicLogin):
    """
    A login class that just uses the standard Django authenticate mechanism
    """

    auth_class = SocialAuthentication


class TokenLogin(account_auth.TokenLogin):
    """
    A login class that returns a user authentication token.  This method, in its default
    configuration is only available if rest_framework.authtoken is in installed_apps
    """

    auth_class = SocialAuthentication


class OAuth2Login(account_auth.OAuth2Login):
    """
    A login class that accepts oauth2 authentication requests and returns the appropriate
    access tokens.  This login method, in its default configuration is only available if
    oauth2_provider is in installed_apps
    """

    auth_class = SocialAuthentication
