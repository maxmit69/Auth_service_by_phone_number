from django.urls import path
from .web_views import RegisterView, VerifyView, UserProfileView

from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/', VerifyView.as_view(), name='verify'),
    path('profile/<uuid:id>/', UserProfileView.as_view(), name='profile'),

]
