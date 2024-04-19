#create a class tools that will contain all functions groq needs
import re
import concurrent.futures
import datetime


class Tools:
    
    def __init__(self, openai_client, groq_client, index):
        self.openai_client = openai_client
        self.groq_client = groq_client
        self.index = index

    def time_to_datetime(self, time):
        hour, minute = time.split(':')
        minute, period = minute.split(' ')
        hour = int(hour)
        minute = int(minute)

        if period == 'PM' and hour != 12:
            hour += 12
        elif period == 'AM' and hour == 12:
            hour = 0

        return datetime.datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)

    def find_classes(self, courses, input_day=datetime.datetime.now().isoweekday(), input_time=datetime.datetime.now().strftime('%I:%M %p').upper()):
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
            start_time = self.time_to_datetime(start_time_str)
            end_time = self.time_to_datetime(end_time_str)
            input_datetime = self.time_to_datetime(input_time)

            return start_time <= input_datetime <= end_time

        for course in courses:
            if is_course_at_time(course['Meetday'], course['Times'], input_day, input_time):
                #current_classes.append(course)
                current_classes.append(f"Course: {course['Course']}\nTitle: {course['Title']}\nProfessor: {course['Professor']}\nTime: {course['Times']}\nLocation: {course['Location']}\n")

        return current_classes

    def extract_text(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return text

    def chunk_text(self, text):
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

    def embed_text(self, text):
        openai_client = self.openai_client
        embedding = openai_client.embeddings.create(input=text, model='text-embedding-3-large').data[0].embedding
        return embedding

    def process_chunk(self, chunk):
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

        vector = self.embed_text(chunk)

        # Convert the vector values to floats and return the result
        return list(map(float, vector))

    def upsert_embeddings(self, chunks):
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
        index = self.index
        openai = self.openai_client
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
                    future = executor.submit(self.process_chunk, chunk, openai)

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

    def retreive_major_info(self, query, chunks):
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
        index = self.index
        try:
            # Generate the query vector using the model
            query_vector = list(map(float, self.embed_text(query)))

            # Perform the query on the index
            results = index.query(vector=query_vector, top_k=1)
            match = results['matches'][0]
            """context = []
            for i, c in enumerate(matches):
                text = chunks[int(c["id"])]
                context.append(text)
                print(f"{i} score: {c["score"]}\n{text}\n\n\n")  """
            text = chunks[int(match['id'])]
            return text

        except Exception as e:
            print("ERROR", e)    
