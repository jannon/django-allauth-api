from rest_framework.response import Response

from allauth.socialaccount import providers
from allauth.socialaccount.adapter import get_adapter

from allauth_api.account.rest_framework.views import CloseableSignupMixin
from .serializers import ProviderSerializer
from allauth import app_settings
from allauth.utils import get_form_class
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.forms import SignupForm
from allauth.socialaccount.helpers import complete_social_signup
from rest_framework.status import HTTP_400_BAD_REQUEST
from allauth_api.settings import allauth_api_settings

APIView = allauth_api_settings.DRF_API_VIEW


class RegisterView(CloseableSignupMixin, APIView):
    """
    Register users who use 3rd-party authentication (e.g. Facebook, Google, Twitter, etc.)
    """

    permission_classes = allauth_api_settings.DRF_REGISTER_VIEW_PERMISSIONS
    form_class = SignupForm

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, 'signup', self.form_class)

    def dispatch(self, request, *args, **kwargs):
        self.sociallogin = None
        data = request.session.get('socialaccount_sociallogin')
        if data:
            self.sociallogin = SocialLogin.deserialize(data)
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def post(self, request, format=None):
        fc = self.get_form_class()
        form = fc(data=request.DATA, files=request.FILES, sociallogin=self.sociallogin)
        if form.is_valid():
            user = form.save(request)
            return complete_social_signup(self.request, user, app_settings.EMAIL_VERIFICATION)
        return Response(form.errors, HTTP_400_BAD_REQUEST)

    def is_open(self):
        return get_adapter().is_open_for_signup(self.request,
                                                self.sociallogin)


register = RegisterView.as_view()


class ProviderListView(APIView):
    """
    List the social account providers available
    """

    permission_classes = allauth_api_settings.DRF_PROVIDERS_VIEW_PERMISSIONS

    def get(self, request, format=None):
        p = providers.registry.get_list()
        serializer = ProviderSerializer(p, many=True)
        return Response(serializer.data)


list_providers = ProviderListView.as_view()
