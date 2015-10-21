from django.utils.translation import ugettext as _

from rest_framework.status import HTTP_304_NOT_MODIFIED, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT,\
    HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from rest_framework.response import Response

from allauth.account.forms import SignupForm, ChangePasswordForm
from allauth.account import app_settings, signals
from allauth.utils import get_user_model, get_form_class

from allauth_api.settings import allauth_api_settings
from .utils import complete_signup
from allauth.account.adapter import get_adapter

import logging
logger = logging.getLogger(__name__)

User = get_user_model()

APIView = allauth_api_settings.DRF_API_VIEW


class AlreadyLoggedInMixin(object):
    """
    Returns a 304 NOT MODIFIED response if the user is already authenticated
    """

    def dispatch(self, request, *args, **kwargs):
        # WORKAROUND: https://code.djangoproject.com/ticket/19316
        self.request = request
        # (end WORKAROUND)
        if request.user.is_authenticated():
            response = Response(None, HTTP_304_NOT_MODIFIED)
            return response
        else:
            response = super(AlreadyLoggedInMixin, self).dispatch(request, *args, **kwargs)
        return response


class LoginHandlerMixin(object):
    """
    Mixin providing common functionality to set login(out) handler
    """

    def post(self, request, *args, **kwargs):
        self.login_handler = None
        login_type = request.data.get('login_type',
                                      allauth_api_settings.DRF_LOGIN_TYPE)
        login_class = allauth_api_settings.DRF_LOGIN_CLASSES[login_type]

        if not login_class:
            return Response({"error": "invalid login type: %s" % login_type}, HTTP_400_BAD_REQUEST)

        self.login_handler = login_class()
        return self.handle_login_logout(request, *args, **kwargs)


class CloseableSignupMixin(object):

    def dispatch(self, request, *args, **kwargs):
        # WORKAROUND: https://code.djangoproject.com/ticket/19316
        self.request = request
        # (end WORKAROUND)
        if not self.is_open():
            return self.closed()
        return super(CloseableSignupMixin, self).dispatch(request,
                                                          *args,
                                                          **kwargs)

    def is_open(self):
        return get_adapter().is_open_for_signup(self.request)

    def closed(self):
        return Response({"message": _("Registration is closed")}, HTTP_403_FORBIDDEN)


class LoginView(AlreadyLoggedInMixin, LoginHandlerMixin, APIView):
    """
    Logs a user in.  The requirements and response will depend on the specific authentication
    mechanism specified in the login_type parameter. Defaults are as follows

    basic - get user_identifier/password from header or post body and auth with django
    session - same as above
    token - get user_identifier/password from header or post body and auth with rest_framework,
            returns token
    oauth2 - input depends on grant type and the oauth2 flow used, returns OAuth2 access token

    social_* - like all the above, but credentials are 3rd-party auth tokens
    """

    permission_classes = allauth_api_settings.DRF_LOGIN_VIEW_PERMISSIONS

    def handle_login_logout(self, request, *args, **kwargs):
        if self.login_handler is None:
            return Response({"message": _("No login handler found")}, HTTP_400_BAD_REQUEST)
        return self.login_handler.login(request, *args, **kwargs)

login = LoginView.as_view()


class LogoutView(LoginHandlerMixin, APIView):
    """
    Logs a user out.
    """

    permission_classes = allauth_api_settings.DRF_LOGOUT_VIEW_PERMISSIONS

    def handle_login_logout(self, request, *args, **kwargs):
        if self.login_handler is None:
            return Response({"message": _("No login handler found")}, HTTP_400_BAD_REQUEST)
        return self.login_handler.logout(request, *args, **kwargs)

logout = LogoutView.as_view()


class RegisterView(CloseableSignupMixin, APIView):
    """
    Registers a new user
    """

    permission_classes = allauth_api_settings.DRF_REGISTER_VIEW_PERMISSIONS
    form_class = SignupForm

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, 'signup', self.form_class)

    def post(self, request, format=None):
        fc = self.get_form_class()
        form = fc(data=request.data, files=request.data)
        if form.is_valid():
            user = form.save(request)
            return complete_signup(self.request, user)
        return Response(form.errors, HTTP_400_BAD_REQUEST)

register = RegisterView.as_view()


class ChangePasswordView(APIView):
    """
    Sets a user's password
    """

    permission_classes = allauth_api_settings.DRF_PASSWORD_VIEW_PERMISSIONS
    form_class = ChangePasswordForm

    def post(self, request, format=None):
        form = self.form_class(data=request.data, user=request.user)
        if form.is_valid():
            form.save()

            signals.password_changed.send(sender=request.user.__class__,
                                          request=request,
                                          user=request.user)
            return Response(None, HTTP_204_NO_CONTENT)
        return Response(form.errors, HTTP_400_BAD_REQUEST)

change_password = ChangePasswordView.as_view()


class RegistrationCheckView(APIView):
    """
    Check if the given user identifier belongs to a registered user
    """

    permission_classes = allauth_api_settings.DRF_REGISTRATIONS_VIEW_PERMISSIONS

    def get(self, request, user_id):
        field_lookup = User.USERNAME_FIELD
        if '@' in user_id:
            field_lookup = 'email'

        if allauth_api_settings.CASE_INSENSITIVE_IDS:
            field_lookup = "%s__iexact" % field_lookup

        try:
            lookup_kwargs = {field_lookup: user_id}
            User.objects.get(**lookup_kwargs)
            return Response(None, HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
                return Response(None, HTTP_404_NOT_FOUND)

check_registration = RegistrationCheckView.as_view()
