from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^register/$", views.register, name="socialaccount_api_register"),
    url(r"^providers/$", views.list_providers, name="socialaccount_api_list_providers"),
]
