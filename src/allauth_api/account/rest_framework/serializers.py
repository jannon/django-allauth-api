from django.contrib.auth import authenticate

from rest_framework import serializers


class UserPassSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        email = attrs.get('email')

        if password and (username or email):
            user = authenticate(username=username, email=email, password=password)

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
            msg = _('Must include "username" or "email", and "password"')
            raise serializers.ValidationError(msg)
