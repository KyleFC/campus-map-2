from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utilities.analysis import get_response
from myapi.tools import Tools

tools_instance = Tools()  # Create an instance of Tools, which manages the initialization of clients.
tools_instance.initialize()  # Initialize the clients for the tools.

@api_view(['POST'])
def process_input(request):
    
    #cursor.execute("SELECT * FROM my_table")
    chatHistory = request.data.get('chatHistory')
    
    response = get_response(message_history=chatHistory, tool=tools_instance)
    response_data = {"finalOutput": response[0], "chatHistory": response[1]}
    
    return Response(response_data)
