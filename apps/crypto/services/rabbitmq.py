import pika
import json
import logging

from rest_framework.response import Response

from django.conf import settings

logger = logging.getLogger(__name__)

def publish_crypto_task(symbol: str):
    '''
    Отправка задачи в очередь
    '''
    
    logger.info(f"Отправка задачи {symbol} в очередь")
    try:
        conn = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    except Exception as e:
        logger.error(f"Ошибка при подключении к RabbitMQ: {str(e)}", exc_info=True)
        return Response({"detail": "Сервис временно недоступен"}, status=503)
    
    ch = conn.channel()
    ch.queue_declare(queue="crypto.tasks", durable=True)
    ch.basic_publish(
        exchange="",
        routing_key="crypto.tasks",
        body=json.dumps({"symbol": symbol})
    )
    conn.close()
    logger.info(f"Задача {symbol} отправлена в очередь")