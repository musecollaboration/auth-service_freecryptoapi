from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.accounts.serializers import MyTokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import validate_password

from drf_spectacular.utils import extend_schema

from apps.accounts.serializers import CreateUserSerializer, ChangePasswordSerializer
from apps.accounts.models import User


class RegisterAPIView(CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    @extend_schema(
        summary="Регистрация пользователя",
        description="Эндпоинт для регистрации пользователя",
    )
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        return Response({"message": "Пользователь успешно зарегистрирован"}, status=201)


class MyTokenObtainPairView(TokenObtainPairView):
    """
     API для получения токена.
    """
    serializer_class = MyTokenObtainPairSerializer


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Изменение пароля",
        description="Эндпоинт для изменения пароля пользователя",
        request=ChangePasswordSerializer                          # добавляем схему запроса сериализатора
    )
    def patch(self, request, *args, **kwargs):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"error": "Старый пароль неверный"}, status=400)

        validate_password(new_password, user)  # Проверка сложности пароля
        user.set_password(new_password)        # Хеширование нового пароля
        user.save()

        return Response({"message": "Пароль успешно изменен"}, status=200)
