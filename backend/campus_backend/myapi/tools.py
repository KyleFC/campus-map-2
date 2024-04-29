import os
from openai import OpenAI
from pinecone import Pinecone
from groq import Groq
from django.db import connections
from django.conf import settings


class Tools:
    def __init__(self):
        self.openai_client = None
        self.groq_client = None
        self.index = None
        self.cursor = None

    def initialize(self):
        if not self.openai_client:
            self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        if not self.groq_client:
            self.groq_client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
        if not self.index:
            pinecone_client = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
            self.index = pinecone_client.Index('concordia')
            print('Index initialized')
        if not self.cursor:
            self.cursor = connections['default'].cursor()
            print('Cursor initialized')

    @property
    def openai(self):
        if not self.openai_client:
            self.initialize()
        return self.openai_client

    @property
    def groq(self):
        if not self.groq_client:
            self.initialize()
        return self.groq_client

    @property
    def pinecone_index(self):
        if not self.index:
            self.initialize()
        return self.index
    
    @property
    def databse_cursor(self):
        if not self.cursor:
            self.initialize()
        return self.cursor

    def query_course_database(self, query):
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "system", "content": """
                        Your job is to create SQL queries based on the user's requested information from a course database for Concordia University Irvine with the following structure:
                        myapi_course
                            crn (varchar): Course Registration Number (e.g. 32112)
                            course_code (varchar): Course Code (e.g. CSC-101-1)
                            title (varchar): Course Title (e.g. HISTORY/LITERATURE OT, FUNDAMENTALS  OF PROGRAMMING)
                            professor (varchar): Professor's Name (e.g. Cserhati, M.)
                            fees (varchar): Course Fees (optional)
                            comments (text): Additional Comments (optional)
                            start_date (varchar): Course Start Date (e.g. 01/01/2024)
                            end_date (varchar): Course End Date (e.g. 05/01/2024)
                        myapi_session
                            id (int): Unique Session ID
                            course_id (int): Foreign Key referencing the Courses table
                            start_date (varchar): Session Start Date (e.g. 01/01/2024)
                            end_date (varchar): Session End Date (e.g. 05/01/2024)
                            meetday (varchar): Day of the week the session meets (optional) (e.g. MWF)
                            start_time (varchar): Session Start Time (optional) (e.g. 9:10 AM)
                            end_time (varchar): Session End Time (optional) (e.g. 4:40 PM)
                            location (varchar): Session Location (e.g. LBART-121)
                        Explain your thoughts step by step
                        You are expected to return the sql query in marks like this ```SELECT * FROM myapi_course WHERE course_code LIKE 'BIO%'```
                        When unsure exactly what the user is asking for you can broaden your query to retrieve more data that would most likely contain what they are looking for.
                        For example, the user may want to know information about an old testament course, but you don't know whether that's the actual name of the course.
                        In this situation you should understand that old testament is most likely a theology course and you should query all theology courses.
                        all course code prefixes:
                        INB
                        MUBT
                        CCI
                        CBIO
                        MUKC
                        MUWC
                        FIN
                        MUBB
                        MUWS
                        PHI
                        SPBU
                        BIO
                        HST
                        CHST
                        MUWO
                        MUGB
                        GRE
                        NPHI
                        MUGU
                        BSC
                        INT
                        HCM
                        MUVB
                        MUVC
                        CENG
                        ACCM
                        ART
                        DCE
                        REL
                        THL
                        PHY
                        MKT
                        MUCO
                        LAT
                        ENG
                        EDLS
                        SPA
                        MUWF
                        MUVH
                        CED
                        KIN
                        MUE
                        DAN
                        NTHL
                        MTH
                        CPHI
                        ANT
                        MUBF
                        SOC
                        HEB
                        ENGR
                        MUWB
                        MUKP
                        ECO
                        ACT
                        IOP
                        EDSP
                        MUS
                        MUVO
                        BDA
                        CHE
                        MACL
                        COM
                        MGT
                        CMTH
                        PSY
                        MUVA
                        POL
                        MUBU
                        MUGC
                        FDVP
                        MUPE
                        MUKO
                        THR
                        NUSA
                        MUKI
                        MUCS
                        MUPD
                        ATHL
                        SCI
                        MUVN
                        WRT
                        EDUC
                        CTHL
                        ARTG
                        GCS
                        BUS
                        CSC
                        Examples:
                           example query: 'All bio courses'
                           expected output: ```SELECT * FROM myapi_course WHERE course_code LIKE 'BIO%'```

                           example query: 'All courses on Monday'
                           expected output: ```SELECT * FROM myapi_session WHERE meetday LIKE '%M%'```
                           
                           example query: 'All courses at 2:00 PM'
                           expected output: ```SELECT * FROM myapi_session WHERE start_time = '2:00 PM'```
                           
                           example query: 'All courses by Professor Smith'
                           expected output: ```SELECT * FROM myapi_course WHERE professor LIKE '%Smith%'```
                           
                           example query: 'All theology classes on Tuesday'
                           expected output: ```SELECT * FROM myapi_session WHERE meetday LIKE '%T%' AND course_id IN (SELECT id FROM Courses WHERE course_code LIKE 'THEO%')```
                           """}, {"role": "user", "content": query}],
                model="llama3-70b-8192"
            )
            response_message = response.choices[0].message.content
            print(response_message)
            #print(response_message)
            if "```" in response_message:
                #if ''' in responsde message then the sql code is likely surrounded by these quotations and we need to extract that sql code
                response_message = response_message.split("```")[1].strip('\n')
                response_message = response_message.strip('sql')
                print('stripped\n')
            self.cursor.execute(response_message)
            print('executed\n')
            if self.cursor is not None:
                output = str(self.cursor.fetchall())
                print(output)
                return output
            return 'No data found'
        
        except Exception as e:
            self.initialize()
            return e
        
    def query_vector_database(self, query):
        print(query)
        index = self.index
        try:
            query_vector = list(map(float, self.embed_text(query)))

            results = index.query(vector=query_vector, top_k=1)
            match = results['matches'][0]
            print(match['id'])
            #ids in pinecone should correspond to filename
            with open(os.path.join(settings.BASE_DIR, f'myapi/data/output_folder{match['id'][:-4]}.txt'), 'r', encoding='utf-8') as f:
                text = f.read()
                f.close()
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "system", "content": f"""
                        Your role is to extract the most relevant information from a given text based on the user query.
                        This information will be used as context or data that can answer multiple questions relating to what the user asked.
                        Context:
                        {text}"""}, {"role": "user", "content": f"Query: {query}"}],
                model="llama3-8b-8192"
            )
            response_message = response.choices[0].message.content
            print("vector response", response_message)
            return response_message
        
        except Exception as e:
            self.initialize()
            print("ERROR", e)    

    def extract_text(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return text

    def embed_text(self, text):
        openai_client = self.openai_client
        embedding = openai_client.embeddings.create(input=text, model='text-embedding-3-large').data[0].embedding
        return embedding

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
            #generate the query vector using the model
            query_vector = list(map(float, self.embed_text(query)))

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

