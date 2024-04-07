from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utilities.analysis import get_response

@api_view(['POST'])
def process_input(request):
    chatHistory = request.data.get('chatHistory')
    # Process the chat history and return the response
    response = get_response(chatHistory)
    response_data = {"finalOutput": response[0], "chatHistory": response[1]}
    
    return Response(response_data)
