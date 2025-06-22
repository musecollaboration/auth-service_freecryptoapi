from django.urls import path

from . import views

urlpatterns = [
    path('', views.CryptoAPIView.as_view(), name='crypto'),
]