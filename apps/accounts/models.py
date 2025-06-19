from django.core.validators import validate_email
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.hashers import check_password

from apps.accounts.managers import CustomUserManager
from apps.common.models import BaseModel


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Модель пользователя
    """
    email = models.EmailField(max_length=255, unique=True, validators=[validate_email])
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email}"


# python manage.py makemigrations
# python manage.py migrate
# python manage.py createsuperuser
# python manage.py shell
