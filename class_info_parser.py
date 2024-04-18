# take in a txt file, chunk the text based on major which is indicated bye Major (major shortened)
# this should result in multiple chunks of text that represent different majors and all of the course descriptions under that major

import re
import os
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
import concurrent.futures

def extract_text_line_by_line(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def parse_major(text):
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

def perform_query(index, query, openai):
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
        results = index.query(vector=query_vector, top_k=5)

        return results

    except Exception as e:
        print("ERROR", e)

if __name__ == "__main__":
    text = extract_text_line_by_line('course_info.txt')
    openai = OpenAI()

    pinecone = Pinecone()
    pinecone.delete_index('campus')
    pinecone.create_index(name='campus', metric='cosine', dimension=3072, spec=ServerlessSpec(cloud='aws', region='us-east-1'))
    index = pinecone.Index('campus')
    chunks = parse_major(text)
    for c in chunks:
        print(len(c))
        print(c.split('\n')[0])

    embedding_list = []
    #print(embed_text("Computer Science", openai))
    upsert_embeddings(index, chunks, openai)
    results = perform_query(index, "Computer Science", openai)
    context = []
    matches = results['matches']
    for i, c in enumerate(matches):
        text = chunks[int(c["id"])]
        context.append(text)
        print(f"{i} score: {c["score"]}\n{text}\n\n\n")              

    