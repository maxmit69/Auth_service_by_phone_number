from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenVerifyView

schema_view = get_schema_view(
    openapi.Info(
        title="Referral System API",
        default_version='v1',
        description="API для реферальной системы",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/', include('users.urls')),
    path('', include('users.web_urls', namespace='web')),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
