from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utilities.analysis import get_response
from campus_backend import openai_client, index, groq_client

@api_view(['POST'])
def process_input(request):
    chatHistory = request.data.get('chatHistory')
    # Process the chat history and return the response
    response = get_response(message_history=chatHistory, groq_client=groq_client, openai_client=openai_client, index=index)
    response_data = {"finalOutput": response[0], "chatHistory": response[1]}
    
    return Response(response_data)
