#from openai import OpenAI
import os
import json
import datetime
from django.conf import settings
from groq import Groq
import re
from pinecone import Pinecone, ServerlessSpec
import concurrent.futures
from openai import OpenAI


#function that interacts with openai api
def get_response(message_history=[]):
    #get analysis_prompt.txt
    file_path = os.path.join(settings.BASE_DIR, 'myapi/utilities/analysis_prompt.txt')

    with open(file_path) as file:
        analysis_prompt = file.read()
        file.close()

    course_file_location = os.path.join(settings.BASE_DIR, 'myapi/data/courses.json')

    with open(course_file_location) as file:
        courses = json.load(file)
        file.close()

    pinecone = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
    pinecone.delete_index('campus')
    pinecone.create_index(name='campus', metric='cosine', dimension=3072, spec=ServerlessSpec(cloud='aws', region='us-east-1'))
    index = pinecone.Index('campus')

    text = extract_text(os.path.join(settings.BASE_DIR, 'myapi/utilities/course_info.txt'))
    chunks = chunk_text(text)

    
    #analysis_prompt = "You are a function calling LLM named Marty that utilizes tools to get information about Concordia University Irvine. Using this information, you will be able to answer questions about the university."
    #message history is a list of dictionaries with the role and content of each message
    #append system message to the front of the list
    #print("Message history start\n", message_history, "Message history end\n")

    if message_history[0]['role'] != 'system':
        message_history.insert(0, {"role": "system", "content": analysis_prompt})
    
    #client = OpenAI()
    client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
    openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
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
                "description": "Perform a query on an index to retreive additional course or major information",
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
                "perform_query": perform_query,
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
    message_history.append({"role": "assistant", "content": final_response})
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

def extract_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def chunk_text(text):
    major_info = ''
    chunks = []
    for line in text.split('\n'):
        # major is indicated by major name (major shortened)
        if re.match(r'(?!\d).*\(([A-Z]{3,})\)$|^([A-Za-z]*: [A-Za-z]*)$', line):
            if major_info:
                chunks.append(f"{major_info}")
            major_info = f'{line}\n'
        else:
            major_info = f"{major_info} {line}"
    return chunks

def embed_text(text, openai_client):
    embedding = openai_client.embeddings.create(input=text, model='text-embedding-3-large').data[0].embedding
    return embedding

def process_chunk(chunk, openai):
    """
    This function processes a chunk of data, transforms it into embeddings using a model,
    and ensures the dimensionality of the resulting vector matches the expected dimensionality.

    Args:
        chunk (str): The chunk of data to be processed.
        model (Model): The model used to transform the chunk into embeddings.
        expected_dim (int): The expected dimensionality of the resulting vector.

    Returns:
        list: The resulting vector with its values converted to floats.
    """

    # Use the model to transform the chunk into embeddings and extract the 'embedding' value

    vector = embed_text(chunk, openai)

    # Convert the vector values to floats and return the result
    return list(map(float, vector))

def upsert_embeddings(index, chunks, openai):
    """
    This function is used to upsert (update or insert) embeddings into a given index.

    Parameters:
    index (object): The index object where the embeddings are to be upserted.
    chunks (list): The list of chunks to be processed.
    model (object): The model used to process the chunks.
    expected_dim (int): The expected dimension of the embeddings.

    Returns:
    None
    """

    try:
        # Create a ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Log the start of the upsert process
            print('upserting vectors...')
            # Initialize an empty list to hold futures
            futures = []

            # Iterate over each chunk
            for i, chunk in enumerate(chunks):
                # Log the current chunk being processed
                print('uploading vector for chunk', i)
                # Submit the chunk to the executor for processing and get a future
                future = executor.submit(process_chunk, chunk, openai)

                # Append the future to the list of futures
                futures.append((str(i), future))

            # Iterate over each future
            for chunk_id, future in futures:
                print('processing chunk', chunk_id)
                # Get the result from the future
                vector = future.result()
                # Upsert the vector into the index
                try:
                    index.upsert(vectors=[(chunk_id, vector)])
                except:
                    print("ERROR")
                print("upserted ", chunk_id)

    except Exception as e:
        # Log any errors that occur during the upsert process
        print("ERROR", e)

def retreive_major_info(index, query, chunks, openai):
    """
    This function performs a query on a given index using a model to generate embeddings.

    Args:
        index: The index to perform the query on.
        query: The query to perform.
        model: The model to use for generating embeddings.
        top_k: The number of top results to return.
        chunks: The chunks of text to search in.

    Raises:
        Exception: If there is an error in the query process.
    """
    try:
        # Generate the query vector using the model
        query_vector = list(map(float, embed_text(query, openai)))

        # Perform the query on the index
        results = index.query(vector=query_vector, top_k=1)
        matches = results['matches']
        """context = []
        for i, c in enumerate(matches):
            text = chunks[int(c["id"])]
            context.append(text)
            print(f"{i} score: {c["score"]}\n{text}\n\n\n")  """
        
        return chunks[int(matches['id'])]

    except Exception as e:
        print("ERROR", e)            

    




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