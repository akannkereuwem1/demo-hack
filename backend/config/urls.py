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
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def test_500_error(request):
    """Temporary view to test 500 errors and logging"""
    # Deliberately raise a generic Python exception
    raise ValueError("This is a deliberate test error for Issue #7!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/test-error/', test_500_error, name='test_error'),
]
