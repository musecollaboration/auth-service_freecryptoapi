import logging
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from apps.crypto.services import redis, rabbitmq, debug_utils
import json
from django.core.cache import caches
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated

tag = 'Курсы криптовалют'
crypto_cache = caches["crypto"]

logger = logging.getLogger(__name__)


class CryptoPriceAPIView(APIView):
    # При тестировании и разработки доступно всем, при необходимости можно ограничить доступ только аутентифицированным
    permission_classes = [AllowAny] if settings.DEBUG else [IsAuthenticated]

    @extend_schema(
        summary="Получение курса криптовалюты",
        description="Эндпоинт для получения курса криптовалюты",
        tags=[tag],
    )
    def get(self, request, symbol):
        symbol = symbol.upper()

        raw = caches["crypto"].get("symbol_map")
        SUPPORTED_SYMBOLS = json.loads(raw) if raw else {}

        if not SUPPORTED_SYMBOLS:
            return Response({"detail": "Символы временно недоступны"}, status=503)

        if symbol not in SUPPORTED_SYMBOLS:
            return Response({"detail": f"Символ не поддерживается: {symbol}"}, status=400)

        price = redis.get_cached_price(symbol)

        if price:
            return Response({"symbol": symbol, "price": price, "source": "cache"})

        # Для тестирования при разработке
        if settings.API_ALLOW_FALLBACK:
            logger.info(f"DEBUG mode: {settings.DEBUG}, Fallback: {settings.API_ALLOW_FALLBACK}, Permissions: {[p.__name__ for p in self.permission_classes]}")

            if not price:
                price = debug_utils.fetch_direct_price(symbol, SUPPORTED_SYMBOLS)

            if price is not None:
                crypto_cache.set(f"crypto:{symbol}", price, timeout=60)  # Кэшируем на 1 минуту только если получили цену, закомментировать при необходимости
                return Response({
                    "symbol": symbol,
                    "price": price,
                    "source": "coingecko (dev fallback)"
                },
                    status=200)

        rabbitmq.publish_crypto_task(symbol)
        return Response({"status": "pending", "retry_after": 3}, status=202)
