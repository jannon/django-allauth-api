from email.mime.image import MIMEImage
from email.utils import make_msgid

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from PIL import Image

from allauth.account import app_settings
from allauth.utils import get_user_model

from allauth_api.settings import allauth_api_settings


class AccountAdapterMixin(object):
    def new_user_response_data(self, user, request=None):
        serializer_class = self.new_user_serializer_class(user)
        return_data = None
        if serializer_class:
            return_data = serializer_class(instance=user, context={'request': request}).data
        return return_data

    def new_user_serializer_class(self, user):
        return None

    def clean_username(self, username, shallow=False):
        """
        Validates the username. You can hook into this if you want to
        (dynamically) restrict what usernames can be chosen. This copies most of the code from the django-allauth
        DefaultAccountAdapter, but adds support for the CASE_INSENTIVE_IDS setting because the PRESERVE_USERNAME_CASING
        setting in allauth, does not allow you to preserve the username case but check against it in a case-insensitive way
        """
        for validator in app_settings.USERNAME_VALIDATORS:
            validator(username)

        # TODO: Add regexp support to USERNAME_BLACKLIST
        username_blacklist_lower = [ub.lower()
                                    for ub in app_settings.USERNAME_BLACKLIST]
        if username.lower() in username_blacklist_lower:
            raise forms.ValidationError(
                self.error_messages['username_blacklisted'])
        # Skipping database lookups when shallow is True, needed for unique
        # username generation.
        if not shallow:
            from .utils import filter_users_by_username
            if filter_users_by_username(username).exists():
                user_model = get_user_model()
                username_field = app_settings.USER_MODEL_USERNAME_FIELD
                error_message = user_model._meta.get_field(
                    username_field).error_messages.get('unique')
                if not error_message:
                    error_message = self.error_messages['username_taken']
                raise forms.ValidationError(error_message)
        return username

    def login(self, request, user):
        super(AccountAdapterMixin, self).login(request, user)
        return {'detail': 'User logged in.'}

    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        if allauth_api_settings.USE_DJANGO_MESSAGES:
            super(AccountAdapterMixin, self).add_message(request, level, message_template, message_context, extra_tags)

    def email_confirmation_key(self, request):
        return request.data.get('key', None)

    def email_confirmation_response_data(self, confirmation):
        return {'detail': '%s %s' % (confirmation.email_address.email, _("confirmed"))}

    def reset_password_confirmation_data(self, request):
        return {
            'uidb36': request.data.get('uidb36', None),
            'key': request.data.get('key', None),
            'password1': request.data.get('password1', None),
            'password2': request.data.get('password2', None),
        }

    def reset_password_confirmation_form_kwargs(self, request):
        return {}

    def reset_password_confirmation_response_data(self, user):
        return {'detail': _("User password changed")}


class ImageKeyMixin(object):
    """
    A mixin class for an account adapter that enables sending and receiving images for email validation
    and password reset keys.
    """

    def render_mail(self, template_prefix, email, context):
        """
        Overrides to catch the prefixes for email confirmation and password reset and render html
        emails with image-based keys
        """
        if template_prefix not in allauth_api_settings.IMAGE_KEY_PREFIXES:
            return super(ImageKeyMixin, self).render_mail(template_prefix, email, context)

        # Create an image key
        gc = allauth_api_settings.IMAGE_KEY_GENERATOR_CLASS
        generator = gc()
        key = self.get_key_from_context(template_prefix, context)
        image = generator.create_image_key(key)
        key_cid = make_msgid()
        context['key_cid'] = key_cid[1:-1]  # trim angle brackets

        subject = render_to_string('{0}_subject.txt'.format(template_prefix),
                                   context)
        # remove superfluous line breaks
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)

        bodies = {}
        for ext in ['html', 'txt']:
            try:
                template_name = '{0}_message.{1}'.format(template_prefix, ext)
                bodies[ext] = render_to_string(template_name,
                                               context).strip()
            except TemplateDoesNotExist:
                # We require both html and text templates
                raise ImproperlyConfigured('Both text and html templates must exist to use ImageKeyMixin')
        msg = EmailMultiAlternatives(subject, bodies['txt'], settings.DEFAULT_FROM_EMAIL, [email])
        msg.attach_alternative(bodies['html'], 'text/html')
        img = MIMEImage(image.read())
        img.add_header('Content-ID', key_cid)
        img.add_header('Content-Disposition', 'inline')
        # msg.attach('key.png', image.read(), 'image/png')
        msg.attach(img)
        image.close()
        return msg

    def get_key_from_context(self, template_prefix, context):
        result = ""
        if 'email_confirmation' in template_prefix:
            result = context['key']
        elif 'password_reset'in template_prefix:
            result = context['password_reset_url'].split('/')[-2]
        return result

    def reset_password_confirmation_data(self, request):
        data = {
            'password1': request.data.get('password1', None),
            'password2': request.data.get('password2', None),
        }
        key_image = request.data.get('key', None)
        if key_image:
            try:
                image = Image.open(key_image)
                key_text = image.text.get('key', None)
                image.close()
            except:
                key_text = key_image  # Fall back on single text key
            if key_text:
                i = key_text.index('-')
                data['uidb36'] = key_text[0:i]
                data['key'] = key_text[i + 1:]

        return data

    def email_confirmation_key(self, request):
        key = None
        key_image = request.data.get('key', None)
        if key_image:
            try:
                key = Image.open(key_image).text.get('key', None)
                key_image.close()
            except:
                key = key_image  # Fall back on text key
        return key
