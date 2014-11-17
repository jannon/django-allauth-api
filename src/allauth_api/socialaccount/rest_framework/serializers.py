from django.contrib.auth import authenticate

from rest_framework import serializers

from allauth.socialaccount.providers.base import Provider


class ProviderSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)

    def restore_object(self, attrs, instance):
        if instance is not None:
            instance.name = attrs.get('name', instance.name)
        return Provider(**attrs)


class OAuth2Serializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, attrs):
        auth_kwargs = self.get_auth_kwargs(attrs)
        user = authenticate(**auth_kwargs)

        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise serializers.ValidationError(msg)
            attrs['user'] = user
            return attrs
        else:
            msg = _('Unable to login with provided credentials.')
            raise serializers.ValidationError(msg)

    def get_auth_kwargs(self, attrs):
        code = attrs.get('code')

        if code:
            return {'code': code}
        else:
            msg = _('Must include "code" parameter')
            raise serializers.ValidationError(msg)
