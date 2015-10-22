from django import forms
from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from allauth.account import app_settings
from allauth.account.adapter import USERNAME_REGEX
from allauth.utils import get_user_model

from allauth_api.settings import allauth_api_settings


class AccountAdapterMixin(object):
    def new_user_response(self, user, request=None):
        serializer_class = self.new_user_serializer()
        return_data = None
        if serializer_class:
            return_data = serializer_class(instance=user, context={'request': request}).data
        return Response(return_data, HTTP_201_CREATED)

    def new_user_serializer(self, user):
        return None

    def clean_username(self, username):
        """
        Validates the username. You can hook into this if you want to
        (dynamically) restrict what usernames can be chosen. This copies most of the code from the django-allauth
        DefaultAccountAdapter, but adds support for the CASE_INSENTIVE_IDS setting
        """
        if not USERNAME_REGEX.match(username):
            raise forms.ValidationError(_("Usernames can only contain "
                                          "letters, digits and @/./+/-/_."))

        # TODO: Add regexp support to USERNAME_BLACKLIST
        username_blacklist_lower = [ub.lower()
                                    for ub in app_settings.USERNAME_BLACKLIST]
        if username.lower() in username_blacklist_lower:
            raise forms.ValidationError(_("Username can not be used. "
                                          "Please use other username."))
        username_field = app_settings.USER_MODEL_USERNAME_FIELD
        assert username_field
        user_model = get_user_model()
        lookup = ''
        if allauth_api_settings.CASE_INSENSITIVE_IDS:
            lookup = '__iexact'
        try:
            query = {username_field + lookup: username}
            user_model.objects.get(**query)
        except user_model.DoesNotExist:
            return username
        raise forms.ValidationError(_("This username is already taken. Please "
                                      "choose another."))
