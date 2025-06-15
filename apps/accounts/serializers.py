from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from apps.accounts.models import User

class CreateUserSerializer(serializers.ModelSerializer):
    account_type = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'account_type')
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            custom_errors = []
            for msg in e.messages:
                if "too short" in msg:
                    custom_errors.append("Пароль слишком короткий, минимум 8 символов")
                elif "too common" in msg:
                    custom_errors.append("Пароль слишком простой и распространённый")
                else:
                    custom_errors.append("Недопустимый пароль")
            raise serializers.ValidationError({"password": custom_errors})
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
