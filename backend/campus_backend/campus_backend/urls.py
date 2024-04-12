"""
URL configuration for campus_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, re_path, include
from django.http import HttpResponse
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage

def serve_react_app(request):
    """Serve `index.html` for non-API routes."""
    index_file_path = settings.BASE_DIR / 'frontend/build/index.html'
    with open(index_file_path, 'rb') as file:
        return HttpResponse(file.read(), content_type='text/html')

urlpatterns = [
    path('api/', include('myapi.urls')),
    re_path(r'^(?!api/).*$', serve_react_app),
]