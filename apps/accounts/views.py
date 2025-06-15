from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin

from apps.accounts.serializers import CreateUserSerializer
from apps.accounts.models import User


class RegisterAPIView(CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(email=response.data["email"])   # Получаем созданного пользователя

        refresh = RefreshToken.for_user(user)                   # Создаем refresh
        access_token = str(refresh.access_token)                # Создаем access

        response.data["access_token"] = access_token            # Добавляем access
        response.data["refresh_token"] = str(refresh)           # Добавляем refresh
        return Response(response.data, status=201)
