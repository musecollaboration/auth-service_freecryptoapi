from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.accounts.serializers import MyTokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from apps.accounts.serializers import CreateUserSerializer, ChangePasswordSerializer, ResetPasswordConfirmSerializer, VerifyEmailSerializer
from apps.accounts.utils import get_user_from_token


from apps.accounts.models import User

from apps.accounts.tasks import verify_email_task, send_reset_password_email_task, reset_password_task


tag = 'Аутентификация'


@method_decorator(ratelimit(key='ip', rate='100/24h', block=True), name='create')  # Ограничение количества запросов 100 раз в 24 часа
class RegisterAPIView(CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    @extend_schema(
        summary="Регистрация пользователя",
        description="Эндпоинт для регистрации пользователя",
        tags=[tag],
    )
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        return Response({"message": "Пользователь успешно зарегистрирован, для активации подтвердите email"}, status=201)


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Эндпоинт для получения токена.
    """
    serializer_class = MyTokenObtainPairSerializer


@method_decorator(ratelimit(key='ip', rate='100/24h', block=True), name='patch')  # Ограничение количества запросов 100 раз в 24 часа
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]    # Только аутентифицированные пользователи могут изменять пароль

    @extend_schema(
        summary="Изменение пароля",
        description="Эндпоинт для изменения пароля пользователя только для аутентифицированных пользователей",
        request=ChangePasswordSerializer,                          # добавляем схему запроса сериализатора
        tags=[tag],
    )
    def patch(self, request, *args, **kwargs):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"error": "Старый пароль неверный"}, status=400)
        elif old_password == new_password:
            return Response({"error": "Старый и новый пароли совпадают"}, status=400)

        validate_password(new_password, user)  # Проверка сложности пароля
        user.set_password(new_password)        # Хеширование нового пароля
        user.save()

        return Response({"message": "Пароль успешно изменен"}, status=200)


@method_decorator(ratelimit(key='ip', rate='100/24h', block=True), name='get')  # Ограничение количества запросов 100 раз в 24 часа
class VerifyEmailView(APIView):
    @extend_schema(
        summary="Подтверждение email",
        description="Эндпоинт для подтверждения email пользователя",
        parameters=[
            OpenApiParameter(
                name="token",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Токен для подтверждения email",
            ),
        ],
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
        tags=[tag],
    )
    def get(self, request):
        """
        Эндпоинт для подтверждения email.
        :param request: запрос
        :return: ответ
        """
        token = request.GET.get("token")
        task_result = verify_email_task.delay(token)  # Запуск задачи для подтверждения email

        return Response({"message": "После подтверждения email вам придет письмо об активации аккаунта"}, status=202)


@method_decorator(ratelimit(key='ip', rate='100/24h', block=True), name='post')  # Ограничение количества запросов 100 раз в 24 часа
class RequestResetPasswordView(APIView):
    """
    Эндпоинт для отправки запроса на сброс пароля.
    """
    @extend_schema(
        summary="Запрос на сброс пароля по email",
        description="Эндпоинт для отправки ссылки на сброс пароля на указанный email",
        request=VerifyEmailSerializer,    # добавляем схему запроса сериализатора
        tags=[tag],
    )
    def post(self, request, *args, **kwargs):
        # Обработка запроса на сброс пароля
        email = request.data.get("email")
        user = User.objects.get_or_none(email=email, is_verified=True)
        if not user:
            raise serializers.ValidationError("Верифицированный пользователь с таким email не найден")

        task_result = send_reset_password_email_task.delay(user.id)  # Запуск задачи для отправки письма

        return Response({"message": "Письмо для сброса пароля отправлено"}, status=200)


@method_decorator(ratelimit(key='ip', rate='100/24h', block=True), name='post')  # Ограничение количества запросов 100 раз в 24 часа
class ResetPasswordConfirmAPIView(APIView):
    """
    Эндпоинт для подтверждения сброса пароля и установки нового.
    """
    @extend_schema(
        summary="Сброс пароля по токену",
        description="Подтверждение сброса пароля и установка нового",
        request=ResetPasswordConfirmSerializer,  # добавляем схему запроса сериализатора
        tags=[tag],
    )
    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("password")

        user = get_user_from_token(token)
        if not user:
            return Response({"error": "Неверный или просроченный токен"}, status=400)

        task_result = reset_password_task.delay(user.id, new_password)  # Запуск задачи для установки нового пароля

        return Response({"message": "Вам придет письмо с подтверждением установки нового пароля"}, status=200)
