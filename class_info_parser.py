# take in a txt file, chunk the text based on major which is indicated bye Major (major shortened)
# this should result in multiple chunks of text that represent different majors and all of the course descriptions under that major

import re
import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
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
        if re.match(r'(?!\d).*\(([A-Z]{3,})\)$', line):
            if major_info:
                chunks.append(major_info)
            major_info = ''
        else:
            major_info = f"{major_info} {line}"
    return chunks

def embed_text(text):
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    embeddings = model.encode(text)
    return embeddings

def process_chunk(chunk):
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
    vector = embed_text(chunk)

    # Convert the vector values to floats and return the result
    return list(map(float, vector))

def upsert_embeddings(index, chunks):
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
                future = executor.submit(process_chunk, chunk)

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

def perform_query(index, query, chunks):
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
        query_vector = list(map(float, embed_text(query)))

        # Perform the query on the index
        results = index.query(vector=query_vector, top_k=5)


        print(results)
        context = []
        for match in results["matches"]:
            # Get the text of the matching chunk
            print(match["id"])
            context.append(chunks[int(match["id"])])
        return context

    except Exception as e:
        print("ERROR", e)

if __name__ == "__main__":
    text = extract_text_line_by_line('course_info.txt')
    pinecone = Pinecone()
    index = pinecone.Index('campus')
    chunks = parse_major(text)
    embedding_list = []

    #upsert_embeddings(index, chunks)
    print(perform_query(index, "Computer Science", chunks))

    