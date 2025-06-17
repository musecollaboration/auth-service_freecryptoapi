
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import User
from apps.accounts.utils import generate_verification_token


@receiver(post_save, sender=User)
def send_verification_signal(sender, instance, created, **kwargs):
    """Отправляет email с подтверждением сразу после создания нового пользователя"""
    if created and not instance.is_verified:
        token = generate_verification_token(instance)

        verification_url = f"{settings.SITE_URL}/auth/verify-email?token={token}"
        subject = "Подтверждение аккаунта"
        message = (
            f"Здравствуйте!\n\n"
            "Спасибо за регистрацию на нашем сайте.\n"
            "Пожалуйста, подтвердите свой аккаунт, перейдя по ссылке ниже (ссылка будет действительна в течение 24 часов):\n\n"
            f"{verification_url}\n\n"
            "Если вы не регистрировались, просто проигнорируйте это письмо.\n\n"
            "С уважением,\nКоманда поддержки Crypto API"
        )

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email], fail_silently=False)
