from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.accounts.models import User
from apps.accounts.tasks import send_verification_email, send_password_changes_email


@receiver(post_save, sender=User)
def send_verification_signal(sender, instance, created, **kwargs):
    """Запускает задачу отправки email с подтверждением сразу после создания нового пользователя"""
    if created and not instance.is_verified:
        send_verification_email.delay(instance.id)


@receiver(pre_save, sender=User)
def send_password_changes(sender, instance, **kwargs):
    """Запускает задачу отправки email с информацией о смене пароля"""
    try:
        old_user = sender.objects.get(id=instance.id)
        if old_user.password != instance.password:
            send_password_changes_email.delay(instance.id)
    except User.DoesNotExist:
        return {"status": "error", "message": "Пользователь не найден"}
