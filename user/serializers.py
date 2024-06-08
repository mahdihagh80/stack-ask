from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password2']
        extra_kwargs = {
                        'email': {'required': True},
                        'first_name': {'required': True},
                        'last_name': {'required': True}
                        }

    def validate(self, data):
        password = data.get('password')
        password2 = data.pop('password2', None)
        if password and not password2:
            raise serializers.ValidationError(
                {'password2': 'must provide password2'}
            )
        if password and password2:
            if password != password2:
                raise serializers.ValidationError(
                    {'password': 'The two password fields didn\'t match.'}
                )

            user = User(**data)
            try:
                validate_password(password, user)
            except exceptions.ValidationError as e:
                raise serializers.ValidationError(
                    {'password': e}
                )
        else:
            data.pop('password', None)

        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)
