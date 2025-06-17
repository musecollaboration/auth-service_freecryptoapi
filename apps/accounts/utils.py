import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings


def generate_verification_token(user):
    """Генерирует JWT-токен для подтверждения email"""
    payload = {
        'user_id': str(user.id),
        'exp': datetime.now(timezone.utc) + timedelta(hours=24),  # Токен с учетом UTC
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
