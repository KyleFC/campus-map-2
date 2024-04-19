import os
from openai import OpenAI
from pinecone import Pinecone
from groq import Groq
from tools import Tools

openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
groq_client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
pinecone_client = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
index = pinecone_client.Index('campus')
print('index initiralized')

Tools = Tools(openai_client, groq_client=groq_client, index=index)