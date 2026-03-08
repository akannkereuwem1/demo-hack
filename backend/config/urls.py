"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

@api_view(['GET'])
@permission_classes([AllowAny])
def test_500_error(request):
    """Temporary view to test 500 errors and logging"""
    # Deliberately raise a generic Python exception
    raise ValueError("This is a deliberate test error for Issue #7!")

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # OpenAPI Schema Configuration
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # JWT Authentication Endpoints
    path('api/auth/token/', extend_schema_view(
        post=extend_schema(
            request=TokenObtainPairSerializer,
            description="Fetch a new pair of access and refresh tokens."
        )
    )(TokenObtainPairView).as_view(), name='token_obtain_pair'),
    
    path('api/auth/token/refresh/', extend_schema_view(
        post=extend_schema(
            request=TokenRefreshSerializer,
            description="Use a valid refresh token to get a new access token."
        )
    )(TokenRefreshView).as_view(), name='token_refresh'),
    
    # App-level routing
    path('api/users/', include('users.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/ai/', include('ai.urls')),
    
    path('api/test-error/', test_500_error, name='test_error'),
]
