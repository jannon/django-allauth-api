from __future__ import absolute_import
import json

from datetime import timedelta

from django import get_version
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

from allauth import app_settings
from allauth_api.settings import allauth_api_settings

from allauth.account.adapter import get_adapter as account_adapter
from allauth.socialaccount.adapter import get_adapter as social_account_adapter
from allauth.socialaccount import providers
try:
    from unittest.case import skipIf, skip
except ImportError:
    from unittest2.case import skipIf, skip

from django.conf.global_settings import INSTALLED_APPS

has_oauth2 = False
has_tokenauth = False

try:
    from oauth2_provider.models import get_application_model
    Application = get_application_model()
    has_oauth2 = True
except ImportError:
    pass

try:
    import rest_framework
    has_tokenauth = True
except ImportError:
    pass

User = get_user_model()

ALL_METHODS = ['OPTIONS', 'HEAD', 'GET', 'PUT', 'PATCH', 'POST', 'DELETE']

user1 = {
            "username": "johndoe",
            "email": "johndoe@example.com",
            "password1": "testpassword",
            "password2": "testpassword"
        }

"""
TODO: tests for authorized api access?

/login/
- token logout
- oauth2 login
- oauth2 logout
- invalid developer

/password/

"""


class BaseAccountsTest(TestCase):
    allowed_methods = ALL_METHODS
    endpoint = '/'
    
    
    def get_endpoint(self):
        return self.endpoint
    
    def get_allowed_methods(self):
        return self.allowed_methods
    
    def get_request_kwargs(self):
        return {}
    
    def test_disallowed_methods(self):
        test_methods = list(set(ALL_METHODS) - set(self.get_allowed_methods()))
        test_url = self.get_endpoint()
        
        for method in test_methods:
            print("%s %s" % (method, test_url))
            request_method = getattr(self.client, method.lower())
            request_kwargs = self.get_request_kwargs()
            
            response = request_method(test_url, **request_kwargs)
            self.assertEqual(response.status_code, 405, "%s request method should not be allowed" % method)
    
    def test_unauthorized_access(self):
        pass
#         response = self.client.get('/social/providers/')
#         print("%d /social/providers" % response.status_code)
#
#         response = self.client.get('/social/register/')
#         print("%d /social/register/" % response.status_code)
# 
#         response = self.client.get('/register/')
#         print("%d /register/" % response.status_code)
#         
#         response = self.client.get('/login/')
#         print("%d /login/" % response.status_code)
#         
#         response = self.client.get('/logout/')
#         print("%d /logout/" % response.status_code)
#         self.assertEqual(response.status_code, 405)


NO_PROVIDER_APPS = list(settings.INSTALLED_APPS)
NO_PROVIDER_APPS.remove('allauth.socialaccount.providers.facebook')
class ProvidersTest(BaseAccountsTest):
    allowed_methods = ['OPTIONS', 'HEAD', 'GET']
    endpoint = '/social/providers/'

    def test_providers(self):
        expected = [{"name": "Facebook"}]
        
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 200, "Non-empty providers list should return 200")
        self.assertJSONEqual(response.content.decode(), json.dumps(expected))
    
    @override_settings(INSTALLED_APPS=NO_PROVIDER_APPS) # until we no lonfer support django < 1.7
    def test_no_providers(self):
        expected = []

# only works in 1.7+
#         with self.modify_settings(INSTALLED_APPS={
#                 'remove': 'allauth.socialaccount.providers.facebook',
#         }):
        # hack the provider registry
        old_registry = providers.registry
        providers.registry = providers.ProviderRegistry()
        
        response = self.client.get(self.endpoint)
        print(response.content)
        self.assertEqual(response.status_code, 200, "Empty providers list should return 200")
        self.assertJSONEqual(response.content.decode(), json.dumps(expected), 
                         "Empty provider list should contain an empty list representation")
        
        providers.registry = old_registry


class RegistrationsTest(BaseAccountsTest):
    allowed_methods = ['OPTIONS', 'HEAD', 'GET']
    endpoint = '/registrations/'
    
    def get_endpoint(self):
        return "%snotauser/" % self.endpoint

    def test_registrations(self):
        user = User.objects.create(username='johndoe', email='johndoe@example.com')
        #user.save()

        response = self.client.get("%s%s/" % (self.endpoint, user.username))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content.decode(), '', "Response should not contain content")
        
        response = self.client.get("%snotauser/" % self.endpoint)
        self.assertEqual(response.status_code, 404)

class RegisterTest(BaseAccountsTest):
    allowed_methods = ['OPTIONS', 'POST']
    endpoint = '/register/'

    def test_register(self):
        # normal valid registration
        response = self.client.post(self.endpoint, user1)
        self.assertEqual(response.status_code, 204)
        
        # existing user
        expected = {
            "email": ["A user is already registered with this e-mail address."],
            "username": ["This username is already taken. Please choose another."]
        }
        response = self.client.post(self.endpoint, user1)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content.decode(), json.dumps(expected))

        # invalid password confirm
        expected = {"__all__": ["You must type the same password each time."]}
        user2 = user1.copy()
        user2.update({
            'username': 'janedoe',
            'email': 'janedoe@example.com',
            'password2': 'blah'
        })
        response = self.client.post(self.endpoint, user2)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content.decode(), json.dumps(expected))

        #missing email address when not required
        user3 = user1.copy()
        user3.update({'username': 'jimmydoe'})
        del user3["email"]
        response = self.client.post(self.endpoint, user3)
        self.assertEqual(response.status_code, 204)
        
        #missing email address when required
        expected = {"email": ["This field is required."]}
        user4 = user1.copy()
        user4.update({'username': 'jennydoe'})
        del user4["email"]
        with self.settings(ACCOUNT_EMAIL_REQUIRED=True):
            response = self.client.post(self.endpoint, user4)
            self.assertEqual(response.status_code, 400)
            self.assertJSONEqual(response.content.decode(), json.dumps(expected))
        
        #missing username
        expected = {"username": ["This field is required."]}
        user5 = user1.copy()
        del user5["username"]
        del user5["email"]
        response = self.client.post(self.endpoint, user5)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content.decode(), json.dumps(expected))

class LoginLogoutTest(BaseAccountsTest):
    allowed_methods = ['OPTIONS', 'POST']
    endpoint="/login/"
    
    def setUp(self):
        user = User.objects.create(username=user1["username"], email=user1["email"])
        user.set_password(user1["password1"])
        user.save()
        
        self.user = user
        self.data = {
            "username": user1["username"],
            "password": user1["password1"],
            "login_type":"basic"
        } 
        self.logout_data = {"login_type":"basic"}

    def tearDown(self):
        self.user.delete()
        self.user = None
        self.data = None
        self.logout_data = None
    
    def test_login_logout(self):
        user = User.objects.get(username=user1["username"])
        
        # normal valid login
        expected={"message": "User logged in."}
        response = self.client.post(self.endpoint, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), json.dumps(expected))
         
        # normal logout
        response = self.client.post("/logout/", self.logout_data)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content.decode(), '')
         
        # not logged in logout
        expected = {'detail': 'Authentication credentials were not provided.'}
        response = self.client.post("/logout/", self.logout_data)
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content.decode(), json.dumps(expected))
         
        # invalid credentials login
        expected = {'message': 'Unable to login with provided credentials.'}
        self.data["password"] = "invalidpassword"
        response = self.client.post(self.endpoint, self.data)
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content.decode(), json.dumps(expected))
         
        # missing credentials login
        expected = {'message': 'Must include "username" or "email", and "password".'}
        del self.data["username"]
        response = self.client.post(self.endpoint, self.data)
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content.decode(), json.dumps(expected))
         
        # --------------------------
        self.user.is_active = False
        self.user.save()
        # --------------------------
         
        #disabled user account login
        expected = {'message': 'User account is disabled.'}
        self.data.update({"password": user1["password1"], "username": user1["username"]})
        response = self.client.post(self.endpoint, self.data)
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content.decode(), json.dumps(expected))
 
        # --------------------------
        self.user.is_active = True
        self.user.save()
        # --------------------------

    
    @skipIf(not has_tokenauth, "rest_framework is not installed")
    def test_token_login_logout(self):
        #token login
        self.data['login_type'] = 'token'
        response = self.client.post(self.endpoint, self.data)
        self.assertEqual(response.status_code, 200)
        obj = json.loads(response.content.decode())
        self.assertIn('message', obj.keys())
        self.assertEqual(obj['message'], 'User logged in.')
        self.assertIn('token', obj.keys())
         
        # token logout
        self.logout_data["login_type"] = "token"
        response = self.client.post("/logout/", self.logout_data)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content.decode(), '')
        
        #TODO Test that user is actually logged out and tokens are revoked

    @skipIf(not has_oauth2, "oauth2_provider is not installed")
    def test_oauth2_login_logout(self):
        #oauth2 invalid client login
        self.data.update({'login_type': 'oauth2', 'grant_type': 'password'})
        response = self.client.post(self.endpoint, self.data)
        self.assertEqual(response.status_code, 401)

        #oauth2 normal login
        
        # regular django login
        self.client.login(**self.data)
        
        # register an application
        app_data = {
            "name": "Test Application",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "client_type": "confidential",
            "authorization_grant_type": "password",
        }
        response = self.client.post(reverse('oauth2_provider:register'), app_data)
        self.assertTrue(response.status_code, 200)
                
        self.client.logout()
        
        # create the authorization header
        import base64
        auth_string = '%s:%s' % ((app_data['client_id'], app_data['client_secret']))
        auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(auth_string.encode()).decode()
        }
        
        # send request
        response = self.client.post(self.endpoint, self.data, **auth_headers)
        print(response.status_code, response.content)
        self.assertEqual(response.status_code, 200)

        # TODO: test implicit application type and just sending client_id (and not secret))
        
        # TODO: test oauth2 logout
        
class PasswordChangeTest(BaseAccountsTest):
    allowed_methods = ['OPTIONS', 'POST']
    endpoint="/password/"
    
    def setUp(self):
        user = User.objects.create(username=user1['username'], email=user1['email'])
        user.set_password(user1['password1'])
        user.save()
        
        self.user = user
        self.data = {
            'password1': 'newpassword',
            'password2': 'newpassword',
            'oldpassword':user1['password1']
        } 
        self.client.login(username=user1['username'], password=user1['password1'])

    def tearDown(self):
        self.client.logout()
        self.user.delete()
        self.user = None
        self.data = None

    