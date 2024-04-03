from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import MyModel
from .serializers import MyModelSerializer  # Add missing import statement

class MyModelList(APIView):
    def get(self, request):
        items = MyModel.objects.all()
        serializer = MyModelSerializer(items, many=True)
        return Response(serializer.data)
