from django.contrib.auth import get_user_model
import django.contrib.auth.password_validation as validators
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    def validate_password(self, data):
        return PasswordSerializer(data={ 'password': data })

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': { 'write_only': True },
        }

class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)

    '''
    Implementing validate_fieldname(self, data) for
    passwords using Django's built-in passwords' validator
    '''
    def validate_password(self, data):
        validators.validate_password(data)
        return data
