from allauth.account.adapter import DefaultAccountAdapter
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from allauth_api.account.rest_framework.adapter import AccountAdapterMixin, ImageKeyMixin


class TestAccountAdapter(AccountAdapterMixin, DefaultAccountAdapter):

    def add_message(self, request, level, message_template, message_context={}, extra_tags=''):
        """
        Don't do anything because the message framework isn't relevant in this Context
        """
        pass

    def new_user_response(self, user, request=None):
        return Response(None, HTTP_204_NO_CONTENT)


class ImageKeyTestAccountAdapter(ImageKeyMixin, AccountAdapterMixin, DefaultAccountAdapter):

    def add_message(self, request, level, message_template, message_context={}, extra_tags=''):
        """
        Don't do anything because the message framework isn't relevant in this Context
        """
        pass

    def new_user_response(self, user, request=None):
        return Response(None, HTTP_204_NO_CONTENT)
