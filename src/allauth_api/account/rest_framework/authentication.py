from django.contrib.auth import logout as auth_logout

from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_204_NO_CONTENT
from rest_framework.response import Response
from rest_framework.authentication import BaseAuthentication, BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed

from allauth.account import app_settings

from .utils import perform_login, RestFrameworkTokenGenerator, serializer_error_string
from .serializers import UserPassSerializer

from oauth2_provider.views.base import TokenView  # , RevokeTokenView

import logging
logger = logging.getLogger(__name__)


class AllAuthMixin(object):

    def authenticate(self, request):
        input_data = self.get_input_data(request)
        serializer = self.serializer_class(data=input_data)
        if serializer.is_valid():
            return (serializer.validated_data['user'], None)
        else:
            raise AuthenticationFailed(serializer_error_string(serializer.errors))


class HeaderDataAuthentication(AllAuthMixin, BaseAuthentication):
    """
    An authentication method that recieves credentials in http headers
    """

    def get_input_data(self, request):
        return request.META


class PostDataAuthentication(AllAuthMixin, BaseAuthentication):
    """
    An authentication method that looks for user credentials in the request data
    """
    serializer_class = UserPassSerializer

    def get_input_data(self, request):
        return request.data


class UserPassAuthentication(BaseAuthentication):
    """
    An authentication method that looks for username/password combination like basic HTTP
    authentication or as simple post parameters
    """

    def authenticate(self, request):
        try:
            result = BasicAuthentication().authenticate(request)
        except AuthenticationFailed:
            pass

        if result is None:
            result = PostDataAuthentication().authenticate(request)
        return result


class BaseLogin(object):
    """
    Base class for a login handler.  All Login handlers should subclass this class
    """

    auth_class = BaseAuthentication

    def login(self, request, *args, **kwargs):
        logger.debug("BaseLogin")
        user = None
        try:
            user, _ = self.authenticate(request)
        except AuthenticationFailed as err:
            return Response({'message': err.detail}, err.status_code)

        if user is not None:
            return perform_login(request, user, email_verification=app_settings.EMAIL_VERIFICATION,
                                 return_data=self.get_return_data(request, user),
                                 signal_kwargs=self.get_signal_kwargs(request, user))
        return Response({'message': 'User authentication failed'}, HTTP_401_UNAUTHORIZED)

    def logout(self, request, **kwargs):
        auth_logout(request)
        return Response(None, HTTP_204_NO_CONTENT)

    def authenticate(self, request, **kwargs):
        return self.auth_class().authenticate(request)

    def get_signal_kwargs(self, request, user):
        return {}

    def get_return_data(self, request, user):
        return {}


class BasicLogin(BaseLogin):
    """
    A login class that just uses the standard Django authentication
    """

    auth_class = UserPassAuthentication


class TokenLogin(BasicLogin):
    """
    A login class that accepts user/pass combinations in header or post data and returns a user
    authentication token.  This method, in its default configuration is only available if
    rest_framework.authtoken is in installed_apps
    """
    token_generator_class = RestFrameworkTokenGenerator

    def get_return_data(self, request, user):
        return {'token': self.token_generator_class().get_token(user).key}

    def logout(self, request, **kwargs):
        self.token_generator_class().revoke_token(request)
        return Response(None, HTTP_204_NO_CONTENT)


class OAuth2Login(BaseLogin):
    """
    A login class that accepts oauth2 authentication requests and returns the appropriate
    access tokens.  This login method, in its default configuration is only available if
    oauth2_provider is in installed_apps
    """

    def login(self, request, *args, **kwargs):
        logger.debug("OAuth2Login")
        view = TokenView.as_view()
        return view(request._request, *args, **kwargs)

    def logout(self, request, **kwargs):
        # TODO: uncomment when update django-oauth-toolkit (only repo has revoke token right now)
        # return RevokeTokenView(request, *args, **kwargs)
        super(self, TokenLogin).logout(request, **kwargs)
