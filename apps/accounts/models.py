from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from apps.accounts.managers import CustomUserManager
from apps.common.models import BaseModel


ACCOUNT_TYPE_CHOICES = (
    ('FREE', 'free_user'),
    ('PREM', 'premium_user'),
    ('ADMIN', 'admin_user'),
)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Модель пользователя
    """
    email = models.EmailField(max_length=255, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default="FREE")

    USERNAME_FIELD = "email"

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} - {self.account_type}"

    def save(self, *args, **kwargs):
        if User.objects.get_or_none(pk=self.pk):
            old_password = User.objects.get(pk=self.pk).password
            if self.password != old_password:
                self.set_password(self.password)
        else:  
            self.set_password(self.password)

        super().save(*args, **kwargs)  


# python manage.py makemigrations
# python manage.py migrate
# python manage.py createsuperuser
# python manage.py shell
