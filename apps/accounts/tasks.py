from apps.accounts.utils import generate_verification_token
from celery import shared_task
import jwt
from django.conf import settings
from django.core.mail import send_mail
import logging
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
import smtplib
import redis
from django.utils import timezone

from apps.accounts.models import User

# Инициализация логгера для отладки и диагностики
logger = logging.getLogger(__name__)


@shared_task
def send_verification_email(user_id):
    """
    celery-задача для отправки писем с подтверждением аккаунта.
    :param user_id: id пользователя, для которого нужно отправить письмо
    :return: словарь с результатом выполнения задачи
    """
    logger.info(f"Отправка письма с подтверждением аккаунта для пользователя id={user_id}")

    try:
        user = User.objects.get(id=user_id)
        token = generate_verification_token(user)

        verification_url = f"{settings.SITE_URL}/api/v1/auth/verify-email?token={token}"
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
        return {"message": "Письмо с подтверждением отправлено", "status": 200}

    except User.DoesNotExist:
        logger.error(f"Пользователь с id={user_id} не найден")
        return {"error": "Пользователь не найден", "status": 404}
    except smtplib.SMTPException as e:
        logger.error(f"Ошибка SMTP при отправке письма: {str(e)}", exc_info=True)
        return {"error": "Ошибка при отправке письма", "status": 500}
    except Exception as e:
        logger.error(f"Неожиданная ошибка при отправке письма с подтверждением: {str(e)}", exc_info=True)
        return {"error": "Произошла неожиданная ошибка при отправке письма с подтверждением", "status": 500}


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
    :return: словарь с результатом выполнения задачи
    """
    logger.info(f"Начало выполнения задачи send_confirmation_email для пользователя {user_id}")
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"Пользователь найден: {user.email}")
        send_mail(
            "Ваш email успешно подтверждён!",
            f"Спасибо, {user.email}, за подтверждение email. Теперь ваш аккаунт активирован.\n\n"
            "С уважением,\nКоманда поддержки Crypto API",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"Письмо успешно отправлено пользователю {user.email}")
    except Exception as e:
        logger.error(f"Ошибка при отправке письма: {str(e)}", exc_info=True)

    logger.info("Задача send_confirmation_email завершена")
    return {"message": "Задача send_confirmation_email завершена", "status": 200}


@shared_task
def send_reset_password_email_task(user_id):
    """
    celery-задача для отправки письма с ссылкой для сброса пароля.
    :param user_id: id пользователя, для которого нужно отправить письмо
    :return: словарь с результатом выполнения задачи
    """
    logger.info(f"Отправка письма с ссылкой для сброса пароля для пользователя id={user_id}")
    try:
        user = User.objects.get(id=user_id)
        token = generate_verification_token(user)
        verification_url = f"{settings.SITE_URL}/api/v1/auth/reset-password-confirm?token={token}"
        subject = "Сброс пароля"
        message = (
            f"Здравствуйте!\n\n"
            "Вы запросили сброс пароля на нашем сайте.\n"
            "Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.\n\n"
            f"Ссылка для сброса пароля: {verification_url}\n\n"
            "С уважением,\nКоманда поддержки Crypto API"
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
        logger.info(f"Письмо с ссылкой для сброса пароля отправлено пользователю id={user_id}")
        return {"message": "Письмо с ссылкой для сброса пароля отправлено", "status": 200}
    except User.DoesNotExist:
        logger.error(f"Пользователь с id={user_id} не найден")
        return {"message": "Пользователь не найден", "status": 404}
    except Exception as e:
        logger.error(f"Ошибка при отправке письма для сброса пароля: {str(e)}", exc_info=True)
        return {"message": "Произошла ошибка при отправке письма", "status": 500}


@shared_task
def reset_password_task(user_id, new_password):
    """
    celery-задача для сброса пароля.
    :param user_id: id пользователя, для которого нужно изменить пароль
    :param new_password: новый пароль
    :return: словарь с результатом выполнения задачи
    """
    logger.info(f"Сброс пароля для пользователя id={user_id}")
    user = User.objects.get(id=user_id)
    try:
        validate_password(new_password, user)  # Проверка сложности пароля
        logger.info(f"Пароль пользователя id={user_id} успешно валидирован")

        user.set_password(new_password)
        user.save()

        send_mail(
            "Ваш пароль успешно изменён!",
            f"Спасибо, {user.email}, за сброс пароля. Теперь ваш пароль активирован.\n\n"
            "С уважением,\nКоманда поддержки Crypto API",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"Пароль пользователя id={user_id} успешно изменен, письмо с подтверждением отправлено")
        return {"status": "success", "message": "Пароль успешно изменен"}
    except serializers.ValidationError as e:
        logger.error(f"Ошибка при валидации пароля: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Неожиданная ошибка при сбросе пароля: {str(e)}", exc_info=True)
        return {"status": "error", "message": "Произошла неожиданная ошибка при сбросе пароля"}


redis_client = redis.StrictRedis(host='localhost', port=6379, db=4)


@shared_task
def send_password_changes_email(user_id):
    """
    Celery-задача для отправки письма с информацией о смене пароля.
    :param user_id: id пользователя, для которого нужно отправить письмо
    :return: словарь с результатом выполнения задачи
    """
    logger.info(f"Запуск задачи отправки письма о смене пароля, user_id={user_id}")

    redis_key = f"password_changed_email_sent:{user_id}"
    if redis_client.get(redis_key):
        logger.warning(f"Письмо уже отправлялось недавно пользователю id={user_id}")
        return {"status": "skipped", "message": "Письмо уже отправлено ранее"}

    try:
        user = User.objects.get(id=user_id)
        current_time = timezone.now().strftime("%d.%m.%Y %H:%M")

        subject = "Информация о смене пароля"
        message = (
            f"Здравствуйте, {user.email}!\n\n"
            f"Ваш пароль был изменён {current_time}.\n"
            f"Если вы не меняли пароль — срочно обратитесь в поддержку.\n\n"
            f"С уважением,\nКоманда поддержки Crypto API"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        redis_client.setex(redis_key, 600, "sent")  # Блокировка на 10 минут
        logger.info(f"Письмо успешно отправлено пользователю id={user_id}")

        return {"status": "success", "message": "Письмо отправлено"}

    except User.DoesNotExist:
        logger.error(f"Пользователь с id={user_id} не найден")
        return {"status": "error", "message": "Пользователь не найден"}

    except Exception as e:
        logger.error(f"Ошибка при отправке письма: {str(e)}", exc_info=True)
        return {"status": "error", "message": "Произошла неожиданная ошибка"}
