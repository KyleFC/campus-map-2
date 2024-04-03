from openai import OpenAI
import os
import json
import datetime
from django.conf import settings

#function that interacts with openai api
def get_response(user_input):
    #get analysis_prompt.txt
    file_path = os.path.join(settings.BASE_DIR, 'backend/campus_backend/myapi/utilities/analysis_prompt.txt')

    with open(file_path) as file:
        analysis_prompt = file.read()
        file.close()
    
    client = OpenAI()
    response = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    messages=[
        {"role": "system", "content": analysis_prompt},
        {"role": "user", "content": user_input},
    ]
    )
    with open('log.txt', 'a') as file:
        file.write(f"{datetime.datetime.now()} - User input: {user_input}\n")
        file.write(f"{datetime.datetime.now()} - Response: {response.choices[0].message.content}\n\n")

    return response.choices[0].message.content