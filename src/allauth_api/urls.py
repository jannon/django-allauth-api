from django.conf.urls import url, patterns, include
from django.utils import importlib

from allauth_api.socialaccount import providers
from allauth import app_settings

urlpatterns = patterns('', url('^', include('allauth_api.account.urls')))

if app_settings.SOCIALACCOUNT_ENABLED:
    urlpatterns += patterns('', url('^social/',
                                    include('allauth_api.socialaccount.urls')))

# for provider in providers.registry.get_list():
#     try:
#         prov_mod = importlib.import_module(provider.package + '.urls')
#     except ImportError:
#         continue
#     prov_urlpatterns = getattr(prov_mod, 'urlpatterns', None)
#     if prov_urlpatterns:
#         urlpatterns += prov_urlpatterns
