from allauth.account.adapter import DefaultAccountAdapter


class TestAccountAdapter(DefaultAccountAdapter):

    def add_message(self, request, level, message_template, message_context={}, extra_tags=''):
        """
        Don't do anything because the message framework isn't relevant in this Context
        """
        pass
