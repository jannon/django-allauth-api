from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _

from rest_framework import serializers


class UserPassSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        email = attrs.get('email')

        if password and (username or email):
            kwargs = {"password": password}
            if username is not None:
                kwargs["username"] = username
            if email is not None:
                kwargs["email"] = email

            user = authenticate(**kwargs)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)
                attrs['user'] = user
                return attrs
            else:
                msg = _('Unable to login with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "username" or "email", and "password".')
            raise serializers.ValidationError(msg)
