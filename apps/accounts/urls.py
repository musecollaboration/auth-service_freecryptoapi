from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from django_ratelimit.decorators import ratelimit
from . import views

urlpatterns = [
    path('', views.RegisterAPIView.as_view({'post': 'create'}), name='register'),
    path('change-password/', views.ChangePasswordAPIView.as_view(), name='change-password'),
    path('verify-email/', views.VerifyEmailView.as_view(), name="verify-email"),

    path('reset-password/', views.RequestResetPasswordView.as_view(), name="reset-password"),
    path('reset-password-confirm/', views.ResetPasswordConfirmAPIView.as_view(), name="reset-password-confirm"),

    path('token/', ratelimit(key='ip', method='POST', rate='100/24h')(views.MyTokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('token/refresh/', ratelimit(key='ip', method='POST', rate='100/24h')(TokenRefreshView.as_view()), name='token_refresh'),
    path('token/verify/', ratelimit(key='ip', method='POST', rate='100/24h')(TokenVerifyView.as_view()), name='token_verify'),
]
