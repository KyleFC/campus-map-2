#from openai import OpenAI
import os
import json
import datetime
from django.conf import settings
from groq import Groq

#function that interacts with openai api
def get_response(message_history=[]):
    #get analysis_prompt.txt
    file_path = os.path.join(settings.BASE_DIR, 'myapi/utilities/analysis_prompt.txt')

    with open(file_path) as file:
        analysis_prompt = file.read()
        file.close()

    courses = json.load(os.path.join(settings.BASE_DIR, 'myapi/data/courses.json'))
    #analysis_prompt = "You are a function calling LLM named Marty that utilizes tools to get information about Concordia University Irvine. Using this information, you will be able to answer questions about the university."
    #message history is a list of dictionaries with the role and content of each message
    #append system message to the front of the list
    #print("Message history start\n", message_history, "Message history end\n")

    if message_history[0]['role'] != 'system':
        message_history.insert(0, {"role": "system", "content": analysis_prompt})
    
    #client = OpenAI()
    client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
    tools = [
        {
            "type": "function",
            "function": {
                "name": "find_classes",
                "description": "Get a json object of the classes that are in session on a given day and time",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "day": {
                            "type": "string",
                            "description": "The day of the week (e.g. 'Monday')",
                        },
                        "time": {
                            "type": "string",
                            "description": "The time of day (e.g. '7:00 PM')",
                        }
                    },
                    "required": ["day", "time"],
                },
            },
        },
    ]

    while True:
        try:
            # Create the completion request
            response = client.chat.completions.create(
                messages=message_history,
                model="mixtral-8x7b-32768",
                tool_choice="auto",
                tools=tools,
            )

            # Get the response message and tool calls
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            # If there are no tool calls, break the loop
            if not tool_calls:
                break

            available_functions = {
                "find_classes": find_classes,
            }
            # Process each tool call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(
                    courses=courses,
                    input_time=function_args.get("time"),
                    input_day=function_args.get("day")
                )
                # Append the function response to the message history
                message_history.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    }
                )
        
        except Exception as e:
            print(e)
            break
    
    # Get the final response
    final_response = response.choices[0].message.content if response else 'No response found.'

    return final_response, message_history[1:]

def time_to_datetime(time):
    hour, minute = time.split(':')
    minute, period = minute.split(' ')
    hour = int(hour)
    minute = int(minute)

    if period == 'PM' and hour != 12:
        hour += 12
    elif period == 'AM' and hour == 12:
        hour = 0

    return datetime.datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)

def find_classes(courses, input_day=datetime.datetime.now().isoweekday(), input_time=datetime.datetime.now().strftime('%I:%M %p').upper()):
    current_classes = []
    days = {'Monday': 'M', 'Tuesday': 'T', 'Wednesday': 'W', 'Thursday': 'R', 'Friday': 'F', 'Saturday': 'S', 'Sunday': 'U',
            0: 'M', 1: 'T', 2: 'W', 3: 'R', 4: 'F', 5: 'S', 6: 'U'}
    
    if input_day in days:
        input_day = days[input_day]
    
    def is_course_at_time(course_day, course_times, input_day, input_time):
        if input_day not in course_day:
            return False
        if course_times == "TBA" or course_times == "By Arrangement":
            return False
        
        start_time_str, end_time_str = course_times.split(' - ')
        start_time = time_to_datetime(start_time_str)
        end_time = time_to_datetime(end_time_str)
        input_datetime = time_to_datetime(input_time)

        return start_time <= input_datetime <= end_time

    for course in courses:
        if is_course_at_time(course['Meetday'], course['Times'], input_day, input_time):
            #current_classes.append(course)
            current_classes.append(f"Class name: {course['Title']}\nProfessor: {course['Professor']}\nTime: {course['Times']}\nLocation: {course['Location']}\n")

    return current_classes

#function that returns the current day and time for the agent
def get_day_time():
    return datetime.datetime.now().isoweekday(), datetime.datetime.now().strftime('%I:%M %p').upper()

if __name__ == '__main__':
        
        with open('C:/Users/epicb/Projects/Campus-Map/campus-map/backend/campus_backend/myapi/data/courses.json') as file:
            courses = json.load(file)
    
        """current_classes = find_classes(courses, "M", "7:00 PM")
    
        print("Current classes at the given time:")
        for course in current_classes:
            print(f"Class name: {course['Title']}\nProfessor: {course['Professor']}\nTime: {course['Times']}\nLocation: {course['Location']}\n")
        """
        sample_message_history = [
            {
                "role": "user",
                "content": "What classes are in session at 9pm on Tuesday?"
            }
        ]
        print(get_response(sample_message_history)[0])