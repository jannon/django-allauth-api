from allauth.account.adapter import DefaultAccountAdapter
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT


class TestAccountAdapter(DefaultAccountAdapter):

    def add_message(self, request, level, message_template, message_context={}, extra_tags=''):
        """
        Don't do anything because the message framework isn't relevant in this Context
        """
        pass

    def new_user_response(self, user, request=None):
        return Response(None, HTTP_204_NO_CONTENT)
