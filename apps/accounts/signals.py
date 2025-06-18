from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import User
from apps.accounts.tasks import send_verification_email


@receiver(post_save, sender=User)
def send_verification_signal(sender, instance, created, **kwargs):
    """Запускает задачу отправки email с подтверждением сразу после создания нового пользователя"""
    if created and not instance.is_verified:
        send_verification_email.delay(instance.id)
