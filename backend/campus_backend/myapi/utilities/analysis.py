from openai import OpenAI
import os
import json
import datetime
from django.conf import settings

#function that interacts with openai api
def get_response(message_history=[]):
    #get analysis_prompt.txt
    file_path = os.path.join(settings.BASE_DIR, 'backend/campus_backend/myapi/utilities/analysis_prompt.txt')

    with open(file_path) as file:
        analysis_prompt = file.read()
        file.close()
        
    #message history is a list of dictionaries with the role and content of each message
    #append system message to the front of the list
    print("Message history start\n", message_history, "Message history end\n")
    message_history.insert(0, {"role": "system", "content": analysis_prompt})
    
    client = OpenAI()
    output = 'No response found.'
    for i in range(11):
        print("Iteration: ", i)
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=message_history)
            #add to chat history the most recent response
            message_history.append({"role": "assistant", "content": response.choices[0].message.content})

            print("Response output: ", response.choices[0].message.content)

            #parse the response to get the command and args
            json_response = json.loads(response.choices[0].message.content)
            command = json_response['command']['name']
            args = json_response['command']['input'] if 'input' in json_response['command'] else None
            output = execute_command(command, args)
            
            print(output)

            
            if type(output) == list:
                # turn output into a string with a newline between each element
                output = '\n'.join([str(elem) for elem in output])
            
            if command in ["final_response", "ask"]:
                print("expecting user response")
                break

        except Exception as e:
            print(e)
            continue

    # Log all chat information and separate lines for debugging
    """with open('log.txt', 'w') as file:
        file.write(f"{datetime.datetime.now()} - User input: {message_history[-2]}\n")
        file.write(f"{datetime.datetime.now()} - Response 1: {message_history[-1]}\n\n")
        file.close()"""

    return output, message_history[1:]

def execute_command(command, args):

    if command == "ask":
        return args['question']
    
    if command == "findCurrentClasses":
        courses = os.path.join(settings.BASE_DIR, 'backend/campus_backend/myapi/data/courses.json')
        with open(courses) as file:
            courses = json.load(file)
        
        if args != None and ('day' in args and 'time' in args):
            classes = find_current_classes(courses, args['day'], args['time'])
        else:
            classes = find_current_classes(courses)
        return  classes
    
    if command == "get_day_time":
        return get_day_time()
    
    if command == 'final_response':
        return args['final_response']
    
    return 'Command not found.'

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

def find_current_classes(courses, input_day=datetime.datetime.now().isoweekday(), input_time=datetime.datetime.now().strftime('%I:%M %p').upper()):
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
            current_classes.append(course)

    return current_classes

#function that returns the current day and time for the agent
def get_day_time():
    return datetime.datetime.now().isoweekday(), datetime.datetime.now().strftime('%I:%M %p').upper()