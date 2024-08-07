from django.urls import path
from .views import RegisterAPIView, VerifyCodeAPIView, UserProfileAPIView


from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api-register'),
    path('verify/', VerifyCodeAPIView.as_view(), name='api-verify'),
    path('profile/<uuid:id>/', UserProfileAPIView.as_view(), name='api-profile'),
]
