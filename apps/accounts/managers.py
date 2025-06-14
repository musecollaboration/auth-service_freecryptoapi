from django.contrib.auth.models import BaseUserManager

from apps.common.managers import GetOrNoneManager


class CustomUserManager(GetOrNoneManager, BaseUserManager):
    """
    Менеджер для создания пользователей
    """

    def create_user(self, email, password, **extra_fields):
        """
        Создает и возвращает пользователя с данными email и паролем.

        :param email: электронная почта
        :param password: пароль
        :param extra_fields: дополнительные поля
        :return: пользователь
        """
        if not email:
            raise ValueError('Email обязателен')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Создает и возвращает администратора.

        :param email: электронная почта
        :param password: пароль
        :param extra_fields: дополнительные поля
        :return: администратор
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('account_type', 'ADMIN')

        return self.create_user(email, password, **extra_fields)
    
