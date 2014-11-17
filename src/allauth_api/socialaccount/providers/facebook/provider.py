from allauth_api.socialaccount.providers import registry
from allauth_api.socialaccount.providers.base import Provider


class FacebookProvider(Provider):
    # TODO
    pass


registry.register(FacebookProvider)
