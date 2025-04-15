# app/embeddings.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from app.utils import split_text_into_chunks

# Initialiseer het embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def build_faiss_index(text: str, chunk_size: int = 500) -> (faiss.IndexFlatL2, list):
    """
    Splitst de tekst in chunks, berekent embeddings en bouwt een FAISS-index.
    Retourneert een tuple: (faiss_index, chunks_list)
    """
    chunks = split_text_into_chunks(text, chunk_size)
    embeddings = model.encode(chunks)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings, dtype=np.float32))
    return index, chunks

def get_query_embedding(query: str):
    """
    Bereken de embedding voor de query.
    """
    return model.encode([query])[0]
