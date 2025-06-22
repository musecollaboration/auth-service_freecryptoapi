from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

import requests


tag = 'Криптовалюты'


class CryptoAPIView(APIView):
    def get(self, request):
        url = "https://api.freecryptoapi.com/v1/getData"
        headers = {
            "X-API-Key": "rczd0a6qo00p17k5dle3"
        }
        params = {
            "symbol": "BTC"
        }

        res = requests.get(url, headers=headers, params=params)

        try:
            data = res.json()
        except ValueError:
            return Response({"error": "Invalid JSON"}, status=502)

        return Response(data, status=res.status_code)
