import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings
import logging

from apps.accounts.models import User

logger = logging.getLogger(__name__)


def generate_verification_token(user):
    """Генерирует JWT-токен для подтверждения email"""
    payload = {
        'user_id': str(user.id),
        'exp': datetime.now(timezone.utc) + timedelta(hours=24),  # Токен с учетом UTC
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def get_user_from_token(token):
    """Извлекает данные из JWT-токена и возвращает объект пользователя"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return User.objects.get(id=payload["user_id"])
    except jwt.ExpiredSignatureError:
        logger.warning("Попытка использования истекшего токена")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Попытка использования недействительного токена")
        return None
    except User.DoesNotExist:
        logger.warning(f"Пользователь из токена не найден в базе данных")
        return None
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке токена: {str(e)}")
        return None
