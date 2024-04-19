import os
import json
from django.conf import settings


#function that interacts with openai api
def get_response(tool=None, message_history=[], ):
    #get analysis_prompt.txt
    openai_client = tool.openai_client 
    groq_client = tool.groq_client
    index = tool.index
    
    file_path = os.path.join(settings.BASE_DIR, 'myapi/utilities/analysis_prompt.txt')

    with open(file_path) as file:
        analysis_prompt = file.read()
        file.close()

    course_file_location = os.path.join(settings.BASE_DIR, 'myapi/data/courses.json')

    with open(course_file_location) as file:
        courses = json.load(file)
        file.close()

    text = tool.extract_text(os.path.join(settings.BASE_DIR, 'myapi/utilities/course_info.txt'))
    chunks = tool.chunk_text(text)

    if message_history[0]['role'] != 'system':
        message_history.insert(0, {"role": "system", "content": analysis_prompt})
    
    
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
        {
            "type": "function",
            "function": {
                "name": "retreive_major_info",
                "description": "Retreive information about a major or course",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The query to perform (e.g. 'Computer Science', 'SCI 115', 'Advanced Research Methods')",
                        },
                    },
                    "required": ["query"],
                },
            },
        },
    ]

    while True:
        try:
            # Create the completion request
            response = groq_client.chat.completions.create(
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
                "find_classes": tool.find_classes,
                "retreive_major_info": tool.retreive_major_info,
            }
            # Process each tool call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                if function_name == "find_classes":
                    function_args = json.loads(tool_call.function.arguments)
                    function_response = function_to_call(
                        courses=courses,
                        input_day=function_args.get("day"),
                        input_time=function_args.get("time"),
                    )
                elif function_name == "retreive_major_info":
                    function_args = json.loads(tool_call.function.arguments)
                    function_response = function_to_call(
                    query=function_args.get("query"),
                    openai=openai_client,
                    index=index,
                    chunks=chunks,
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
    final_response = final_response.strip("</s>") #groq bug fix
    message_history.append({"role": "assistant", "content": final_response})
    return final_response, message_history[1:]        
    




if __name__ == '__main__':
        from groq import Groq
        from pinecone import Pinecone
        from openai import OpenAI

        with open('C:/Users/epicb/Projects/Campus-Map/campus-map/backend/campus_backend/myapi/data/courses.json') as file:
            courses = json.load(file)
        openai_client = OpenAI(api_key="")
        groq_client = Groq(api_key="")
        pinecone_client = Pinecone(api_key="")
        index = pinecone_client.Index('campus')
        """current_classes = find_classes(courses, "M", "7:00 PM")
    
        print("Current classes at the given time:")
        for course in current_classes:
            print(f"Class name: {course['Title']}\nProfessor: {course['Professor']}\nTime: {course['Times']}\nLocation: {course['Location']}\n")
        """
        sample_message_history = [
            {
                "role": "user",
                "content": "Can you tell me more about Concordia's computer science major?"
            }
        ]
        print(get_response(openai_client=openai_client, index=index, message_history=sample_message_history, groq_client=groq_client, )[0])