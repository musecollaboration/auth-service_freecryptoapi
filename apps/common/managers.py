from django.db import models


class GetOrNoneQuerySet(models.QuerySet):
    """Пользовательский запрос, который поддерживает get_or_none()"""

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class GetOrNoneManager(models.Manager):
    """Добавляет метод get_or_none к объектам"""

    def get_queryset(self):
        return GetOrNoneQuerySet(self.model)

    def get_or_none(self, **kwargs):
        return self.get_queryset().get_or_none(**kwargs)
