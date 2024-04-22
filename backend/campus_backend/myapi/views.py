from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utilities.analysis import get_response
from tools import Tools
from django.db import connections

tools_instance = Tools()  # Create an instance of Tools, which manages the initialization of clients.

@api_view(['POST'])
def process_input(request):
    
    cursor = connections['readonly'].cursor()
    #cursor.execute("SELECT * FROM my_table")
    chatHistory = request.data.get('chatHistory')
    
    response = get_response(message_history=chatHistory, tool=tools_instance, data_cursor=cursor)
    response_data = {"finalOutput": response[0], "chatHistory": response[1]}
    
    return Response(response_data)
