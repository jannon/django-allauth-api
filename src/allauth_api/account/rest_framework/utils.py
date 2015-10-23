from django.conf import settings
from allauth.account.app_settings import EmailVerificationMethod
from allauth.account.utils import send_email_confirmation, get_adapter, messages, signals
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED)
from django.core.exceptions import ImproperlyConfigured


class BaseTokenGenerator(object):
    """
    Base class for things generating tokens for user authentication
    """

    def get_token(self, user):
        raise NotImplementedError("subclass and implement")

    def revoke_token(self, user):
        raise NotImplementedError("subclass and implement")


class RestFrameworkTokenGenerator(BaseTokenGenerator):
    """
    Class that creates/retrieves rest_framework.authtoken.Token tokens for users
    """

    def __init__(self):
        if 'rest_framework.authtoken' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured('rest_framework.auth_token must be in installed_apps')

    def get_token(self, user):
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=user)
        return token

    def revoke_token(self, request):
        from rest_framework.authtoken.models import Token
        token = None
        try:
            token = Token.objects.get(user=request.user)
        except:
            pass
        if token is not None:
            token.delete()


def perform_login(request, user, email_verification, return_data=None, signal_kwargs={},
                  signup=False):
    """
    Keyword arguments:

    signup -- Indicates whether or not sending the
    email is essential (during signup), or if it can be skipped (e.g. in
    case email verification is optional and we are only logging in).
    """
    from allauth.account.models import EmailAddress
    has_verified_email = EmailAddress.objects.filter(user=user,
                                                     verified=True).exists()
    if email_verification == EmailVerificationMethod.NONE:
        pass
    elif email_verification == EmailVerificationMethod.OPTIONAL:
        # In case of OPTIONAL verification: send on signup.
        if not has_verified_email and signup:
            send_email_confirmation(request, user, signup=signup)
    elif email_verification == EmailVerificationMethod.MANDATORY:
        if not has_verified_email:
            send_email_confirmation(request, user, signup=signup)
            return Response({'message': 'Account email verification sent'}, HTTP_401_UNAUTHORIZED)
    # Local users are stopped due to form validation checking
    # is_active, yet, adapter methods could toy with is_active in a
    # `user_signed_up` signal. Furthermore, social users should be
    # stopped anyway.
    if not user.is_active:
        return Response({'message': 'User account is inactive'}, HTTP_403_FORBIDDEN)

    if return_data is None:
        return_data = {}
    login_data = get_adapter().login(request, user)
    signals.user_logged_in.send(sender=user.__class__,
                                request=request,
                                user=user,
                                **signal_kwargs)
    get_adapter().add_message(request,
                              messages.SUCCESS,
                              'account/messages/logged_in.txt',
                              {'user': user})

    return_data.update(login_data or {})
    status_code = HTTP_200_OK
    if signup:
        status_code = HTTP_201_CREATED
    return Response(return_data, status_code)


def complete_signup(request, user, email_verification, signal_kwargs=None):
    if signal_kwargs is None:
        signal_kwargs = {}
    signals.user_signed_up.send(sender=user.__class__,
                                request=request,
                                user=user,
                                **signal_kwargs)

    return_data = get_adapter().new_user_response_data(user, request=request)
    return perform_login(request, user,
                         email_verification=email_verification,
                         return_data=return_data,
                         signal_kwargs=signal_kwargs,
                         signup=True)


def serializer_error_string(errors):
    errlist = []

    for k in errors:
        if k == 'non_field_errors':
            for v in errors[k]:
                errlist.append(v)
        else:
            for v in errors[k]:
                errlist.append("%s - %s" % (k, v))
    return "\n".join(errlist)
