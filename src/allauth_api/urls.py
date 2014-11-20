from django.conf.urls import url, patterns, include
from allauth import app_settings
from allauth_api.settings import allauth_api_settings

api_mod_name = allauth_api_settings.API_FRAMEWORK

urlpatterns = patterns("", url(r"^", include('allauth_api.account.' + api_mod_name + '.urls')))

if app_settings.SOCIALACCOUNT_ENABLED:
    urlpatterns += patterns("", url(r"^social/",
                                    include('allauth_api.socialaccount.' + api_mod_name + '.urls')))

# for provider in providers.registry.get_list():
#     try:
#         prov_mod = importlib.import_module(provider.package + '.urls')
#     except ImportError:
#         continue
#     prov_urlpatterns = getattr(prov_mod, 'urlpatterns', None)
#     if prov_urlpatterns:
#         urlpatterns += prov_urlpatterns
