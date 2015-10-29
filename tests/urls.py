from django.conf.urls import patterns, url, include
from views import EmailRequiredView

urlpatterns = patterns("",
    url(r'^', include('allauth_api.urls')),
    url(r'^test', include('allauth.urls')),
    url(r'^email_required/$', EmailRequiredView.as_view(), name='account_api_email_required')
)

try:
    import oauth2_provider  # NOQA
except ImportError:
    pass
else:
    urlpatterns += patterns("",
        url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    )
