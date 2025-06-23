import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def fetch_direct_price(symbol, symbol_map):
    '''
    Получение курса криптовалюты напрямую с coingecko для тестирования
    '''
    url = f"https://api.coingecko.com/api/v3/simple/price"
    headers = {"x-cg-api-key": settings.COINGECKO_API_KEY}
    coingecko_id = symbol_map.get(symbol)
    logger.info(f"coingecko_id: {coingecko_id}")

    params = {
        "ids": coingecko_id,
        "vs_currencies": "usd",
        }
    result = requests.get(url, headers=headers, params=params)
    try:
        data = result.json()
        price = data.get(coingecko_id, {}).get("usd")
        return price
    except ValueError as e:
        logger.error(f"Ошибка при fallback-запросе: {e}", exc_info=True)
        return None
