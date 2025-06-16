from rest_framework_simplejwt.views import TokenObtainPairView
from apps.accounts.serializers import MyTokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin

from apps.accounts.serializers import CreateUserSerializer
from apps.accounts.models import User


class RegisterAPIView(CreateModelMixin, GenericViewSet):
    """
    Представление для регистрации пользователя.
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        """
        Создает пользователя
        """
        response = super().create(request, *args, **kwargs)
        return Response({"message": "Пользователь успешно зарегистрирован"}, status=201)


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Представление для получения токена.
    """
    serializer_class = MyTokenObtainPairSerializer
