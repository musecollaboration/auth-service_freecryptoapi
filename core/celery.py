import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения для корректной работы Celery с Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Инициализация экземпляра Celery
app = Celery('core')

# Конфигурация из `settings.py`, все параметры должны начинаться с `CELERY_`
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач из `tasks.py` во всех приложениях Django
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'delete-unverified-users-every-day': {
        'task': 'apps.accounts.tasks.delete_unverified_users',
        'schedule': crontab(hour=0, minute=0),  # Выполнять каждый день в полночь
    },
}
