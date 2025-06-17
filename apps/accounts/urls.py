from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

urlpatterns = [
    path('', views.RegisterAPIView.as_view({'post': 'create'}), name='register'),
    path('change-password', views.ChangePasswordAPIView.as_view(), name='change-password'),
    path('verify-email/', views.VerifyEmailView.as_view(), name="verify-email"),

    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
