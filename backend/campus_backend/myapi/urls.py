from django.urls import include, path
from .views import process_input

urlpatterns = [
    path('openai/', process_input, name='process_input'),
]
