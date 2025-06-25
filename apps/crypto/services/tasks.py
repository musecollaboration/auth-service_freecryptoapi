import requests
import json
from django.core.cache import caches
from celery import shared_task


@shared_task
def fetch_supported_symbols(pages=4):
    '''
    Получение symbol_map из CoinGecko /coins/markets (по страницам)
    '''
    url = "https://api.coingecko.com/api/v3/coins/markets"
    symbol_map = {}

    for page in range(1, pages + 1):
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": page,
            "sparkline": False
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            continue

        data = response.json()
        for entry in data:
            symbol = entry["symbol"].upper()
            if symbol not in symbol_map:  # берём только первого (с большим cap'ом)
                symbol_map[symbol] = entry["id"]

    caches["crypto"].set("symbol_map", json.dumps(symbol_map), timeout=86400)  # кэшируем на 24 часа
    return f"{len(symbol_map)} symbols saved"
