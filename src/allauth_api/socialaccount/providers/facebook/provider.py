from allauth_api.socialaccount.providers import registry
from allauth_api.socialaccount.providers.base import Provider


class FacebookProvider(Provider):
    id = 'facebook'


registry.register(FacebookProvider)
