from rest_framework.permissions import BasePermission, SAFE_METHODS

from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation

from allauth_api.settings import allauth_api_settings


class EmailVerified(BasePermission):
    def has_permission(self, request, view):
        if not EmailAddress.objects.filter(user=request.user, verified=True).exists():
            if allauth_api_settings.AUTO_SEND_EMAIL_CONFIRMATION:
                send_email_confirmation(request, request.user)
            return False
        return True


class EmailVerifiedOrReadOnly(EmailVerified):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS or
                super(EmailVerifiedOrReadOnly, self).has_permission(request, view))
