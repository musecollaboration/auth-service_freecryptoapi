from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.fields import UUIDField


from apps.accounts.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания пользователя
    """
    id = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = str(instance.id)
        return representation

    class Meta:
        model = User
        fields = ('id', 'email', 'password')                     # Поля для сериализации
        extra_kwargs = {"password": {"write_only": True}}  # Скрытие пароля

    def validate_password(self, value):
        """
        Валидация пароля. Генерирует ошибку, если пароль слишком короткий
        (менее 8 символов), или слишком простой (too common).
        """
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


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Сериализатор для получения токена
    """
    @classmethod
    def get_token(cls, user):
        """
        Возвращает токен для указанного пользователя
        :param user: пользователь
        :return: токен
        """
        token = super().get_token(user)
        token['account_type'] = user.account_type    # Добавление поля account_type в токен

        return token

    def validate(self, attrs):
        """
        Валидация переданных данных. Если пользователь не подтверждён, то генерирует ошибку.
        :param attrs: словарь с данными
        :return: словарь с данными
        """
        data = super().validate(attrs)

        user = self.user
        if not user.is_verified:
            raise serializers.ValidationError("Аккаунт не подтверждён. Проверьте почту и активируйте профиль.")

        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Сериализатор для изменения пароля
    """
    old_password = serializers.CharField(help_text="Введите ваш текущий пароль")
    new_password = serializers.CharField(help_text="Введите ваш новый пароль")


class VerifyEmailSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения email
    """
    email = serializers.EmailField()


class ResetPasswordConfirmSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения сброса пароля
    """
    token = serializers.CharField()
    password = serializers.CharField()
