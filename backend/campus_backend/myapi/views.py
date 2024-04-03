from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utilities.analysis import get_response

@api_view(['POST'])
def process_input(request):
    user_input = request.data.get('userInput')
    # Process the user input here and generate a response
    response_data = {"finalOutput": get_response(user_input)}
    return Response(response_data)
