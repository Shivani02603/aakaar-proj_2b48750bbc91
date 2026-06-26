import os
from typing import List
import openai

# Constants
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

def embed_text(text: str) -> List[float]:
    """
    Embed a single text string using the pinned embedding model.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    
    client = openai.OpenAI(api_key=api_key)
    response = client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
    return response.data[0].embedding

def embed_batch(texts: List[str]) -> List[List[float]]:
    """
    Embed a batch of text strings using the pinned embedding model.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    
    client = openai.OpenAI(api_key=api_key)
    response = client.embeddings.create(input=texts, model=EMBEDDING_MODEL)
    return [item.embedding for item in response.data]

def get_embedding(texts: List[str]) -> List[List[float]]:
    """
    Module-level function to embed a batch of text strings.
    """
    return embed_batch(texts)