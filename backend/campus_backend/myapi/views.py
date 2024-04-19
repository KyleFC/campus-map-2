from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utilities.analysis import get_response
from campus_backend import Tools

@api_view(['POST'])
def process_input(request):
    chatHistory = request.data.get('chatHistory')
    
    response = get_response(message_history=chatHistory, tool=Tools)
    response_data = {"finalOutput": response[0], "chatHistory": response[1]}
    
    return Response(response_data)
