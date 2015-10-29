from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase

from allauth.account.models import EmailAddress

PASSWORD = "secrets!"


class EmailRequiedPermissionTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='johndoe', email='johndoe@example.com')
        self.user2 = User.objects.create(username='janedoe', email='janedoe@example.com')
        self.user1.set_password(PASSWORD)
        self.user1.save()
        self.user2.set_password(PASSWORD)
        self.user2.save()

        EmailAddress.objects.create(user=self.user1, email=self.user1.email, primary=True, verified=True)
        EmailAddress.objects.create(user=self.user2, email=self.user2.email, primary=True)

    def test_verified_email(self):
        self.client.login(username=self.user1.username, password=PASSWORD)
        response = self.client.get(reverse('account_api_email_required'))
        self.assertEqual(response.status_code, 200)

    def test_unverified_email(self):
        self.client.login(username=self.user2.username, password=PASSWORD)
        response = self.client.get(reverse('account_api_email_required'))
        self.assertEqual(response.status_code, 403)
