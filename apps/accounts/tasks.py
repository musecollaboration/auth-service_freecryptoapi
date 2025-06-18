from apps.accounts.utils import generate_verification_token
from celery import shared_task
import jwt
from django.conf import settings
from django.core.mail import send_mail
import logging

from apps.accounts.models import User

# Инициализация логгера для отладки и диагностики
logger = logging.getLogger(__name__)


@shared_task
def send_verification_email(user_id):
    """
    celery-задача для отправки писем с подтверждением аккаунта.
    :param user_id: id пользователя, для которого нужно отправить письмо
    :return: None
    """
    
    logger.info(f"Отправка письма с подтверждением аккаунта для пользователя id={user_id}")

    user = User.objects.get(id=user_id)
    token = generate_verification_token(user)

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

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
    logger.info(f"Письмо с подтверждением отправлено пользователю id={user_id}")


@shared_task
def verify_email_task(token):
    """
    celery-задача для подтверждения email.
    :param token: jwt-токен, содержащий информацию о пользователе
    :return: словарь с результатом выполнения задачи
    """
    logger.info(f"Начало выполнения задачи verify_email_task")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user = User.objects.get(id=payload["user_id"])
        user.is_verified = True
        user.save()
        task = send_confirmation_email.delay(user.id)
        logger.info(f"Задача отправки письма добавлена в очередь. ID задачи: {task.id}")
        return {"message": "После подтверждения email придет письмо об активации аккаунта", "status": 200}
    except jwt.ExpiredSignatureError:
        return {"error": "Токен истёк", "status": 400}
    except jwt.InvalidTokenError:
        return {"error": "Некорректный токен", "status": 400}
    except Exception as e:
        logger.error(f"Ошибка при верификации email: {str(e)}", exc_info=True)
        return {"error": "Произошла ошибка при верификации email", "status": 500}


@shared_task
def send_confirmation_email(user_id):
    """
    celery-задача для отправки писем с подтверждением email.
    :param user_id: id пользователя, для которого нужно отправить письмо
    :return: None
    """
    logger.info(f"Начало выполнения задачи send_confirmation_email для пользователя {user_id}")
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"Пользователь найден: {user.email}")
        send_mail(
            "Ваш email успешно подтверждён!",
            f"Спасибо, {user.email}, за подтверждение email. Теперь ваш аккаунт активирован.",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"Письмо успешно отправлено пользователю {user.email}")
    except Exception as e:
        logger.error(f"Ошибка при отправке письма: {str(e)}", exc_info=True)

    logger.info("Задача send_confirmation_email завершена")
