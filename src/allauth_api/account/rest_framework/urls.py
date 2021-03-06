from django.conf.urls import url

from . import views
from oauth2_provider.views.base import TokenView, RevokeTokenView

urlpatterns = [
    url(r"^register/$", views.register, name="account_api_register"),
    url(r"^registrations/(?P<user_id>[^/]+)/$", views.check_registration, name="account_api_check_registration"),
    url(r"^send-email-confirmation/$", views.send_email_confirmation, name="account_api_send_email_confirmation"),
    url(r"^confirm-email/$", views.confirm_email, name="account_api_confirm_email"),
    url(r"^login/$", views.login, name="account_api_login"),
    url(r"^oauth-login/$", TokenView.as_view(), name="account_api_oauth2_login"),
    url(r"^logout/$", views.logout, name="account_api_logout"),
    url(r"^oauth-logout/$", RevokeTokenView, name="account_api_oauth2_logout"),
    url(r"^password/$", views.change_password, name="account_api_change_password"),
    url(r"^password/reset/$", views.reset_password, name="account_api_reset_password"),
    url(r"^password/reset/confirm/$", views.confirm_reset_password, name="account_api_reset_password_confirm"),
]
