from django.urls import path

from . import views

urlpatterns = [
    path("price/<str:symbol>/", views.CryptoPriceAPIView.as_view(), name="crypto-price"),
]