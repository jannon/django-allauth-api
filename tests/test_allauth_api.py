from __future__ import absolute_import
import json

from datetime import timedelta

from django.utils.timezone import now
from django.test.utils import override_settings
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.core import mail
from django.contrib.sites.models import Site
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser

from allauth.utils import get_user_model

from . import app_settings

from allauth.account.adapter import get_adapter as account_adapter
from allauth.socialaccount.adapter import get_adapter as social_account_adapter
from billiard.tests.utils import Case

User = get_user_model()

ALL_METHODS = ['OPTIONS', 'HEAD', 'GET', 'PUT', 'PATCH', 'POST', 'DELETE']

"""
/providers/
- normal case
- no providers
- bad methods (common)
- unauthorized (common)

/registrations/
- existing user
- non-existing user
- invalid user_id
- bad methods(common)
- unauthorized (common)


"""


class BaseAccountsTest(TestCase):
    allowed_methods = ALL_METHODS
    endpoint = '/'
    
    
    def get_endpoint(self):
        return self.endpoint
    
    def get_allowed_methods(self):
        return self.allowed_methods
    
    def test_disallowed_methods(self):
        test_methods = list(set(ALL_METHODS) - set(self.get_allowed_methods()))
        test_url = self.get_endpoint()
        
        
    
    def test_unauthorized_access(self):
        pass


class ProvidersTest(BaseAccountsTest):
    allowed_methods = ['OPTIONS', 'HEAD', 'GET'] 