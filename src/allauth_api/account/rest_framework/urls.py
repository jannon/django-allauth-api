from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    "",
    url(r"^register/$", views.register, name="account_api_register"),
    url(r"^registrations/(?P<user_id>[^/]+)/$", views.check_registration,
        name="account_api_check_registration"),
    url(r"^login/$", views.login, name="account_api_login"),
    url(r"^logout/$", views.logout, name="account_api_logout"),
    url(r"^password/$", views.change_password,
        name="account_api_change_password"),
    #     url(r"^password/reset/$", views.reset_password,
    #         name="account_api_reset_password"),
    #     url(r"^password/reset/confirm/$", views.confirm_reset_password,
    #         name="account_api_reset_password_confirm"),
)
