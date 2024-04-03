from django.urls import include, path
from .views import MyModelList

urlpatterns = [
    path('api/my-model/', MyModelList.as_view()),
    path('', include('myapi.urls')),
]
