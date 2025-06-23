from django.core.cache import caches
import logging

logger = logging.getLogger(__name__)

crypto_cache = caches["crypto"]


def get_cached_price(symbol):
    '''
    Получение курса криптовалюты из кэша
    '''
    logger.info(f"Получение курса криптовалюты {symbol} из кэша")
    result = crypto_cache.get(f"crypto:{symbol}")
    if not result:
        logger.info(f"Курс криптовалюты {symbol} не найден в кэше, обращение к API")
        return None
    
    logger.info(f"Курс криптовалюты {symbol} получен из кэша")
    return result
