import os
from openai import OpenAI
from pinecone import Pinecone

openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
pinecone_client = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))