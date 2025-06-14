import uuid
from django.db import models

from apps.common.managers import GetOrNoneManager



class BaseModel(models.Model):
    """
    Базовый класс, который включает в себя общие поля и методы для всех моделей.

    Attributes:
        id (UUIDField): Уникальный идентификатор записи.
        created_at (DateTimeField): Дата и время создания записи.
        updated_at (DateTimeField): Дата и время обновления записи.
    """
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = GetOrNoneManager()

    class Meta:
        abstract = True

