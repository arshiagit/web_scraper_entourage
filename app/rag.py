# app/rag.py
import numpy as np
import faiss
from app.embeddings import get_query_embedding
import logging
from dotenv import load_dotenv
import os
from openai import OpenAI
import time

# Configuratie van logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialiseer de OpenAI API client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Functie om relevante chunks op te halen
def retrieve_relevant_chunks(query: str, index: faiss.IndexFlatL2, chunks: list, top_k: int = 5, batch_size: int = 10) -> list:
    """
    Haal de meest relevante chunks op uit de FAISS-index, rekening houdend met het opgegeven aantal resultaten (top_k).
    Batch verwerking kan schaalbaarheid verbeteren.
    """
    query_embedding = get_query_embedding(query)
    
    try:
        # Batch zoekopdrachten kunnen de prestaties verbeteren bij grotere hoeveelheden data
        D, I = index.search(np.array([query_embedding], dtype=np.float32), top_k)
        
        relevant_chunks = [chunks[i] for i in I[0] if i < len(chunks)]
        logger.info(f"Found {len(relevant_chunks)} relevant chunks for query: '{query}'")
        return relevant_chunks

    except Exception as e:
        logger.error(f"Error retrieving relevant chunks: {str(e)}")
        raise e

# Functie om een antwoord te genereren op basis van de opgehaalde chunks
def generate_answer(query: str, context_chunks: list, max_tokens: int = 150) -> str:
    """
    Genereer een antwoord op basis van de opgehaalde relevante chunks met behulp van de OpenAI API.
    """
    if not context_chunks:
        logger.warning("No relevant context found for the query.")
        return "Er is geen relevante context gevonden voor je vraag."

    context = "\n---\n".join(context_chunks)
    prompt = (
        f"Gebruik uitsluitend onderstaande context om de vraag te beantwoorden. "
        f"Doorzoek de context om de meest relevante informatie te vinden.\n\n"
        f"Context:\n{context}\n\n"
        f"Vraag:\n{query}\n\n"
        f"Antwoord (in het Nederlands):"
    )

    logger.info(f"Generating answer for query: '{query}' with {len(context_chunks)} context chunks.")
    
    try:
        # Call to OpenAI API (let op: aangepaste API-aanroep voor GPT-4)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[ 
                {"role": "system", "content": "Je bent een behulpzame assistent."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )

        # Verwerking van het antwoord
        answer = response.choices[0].message.content.strip()
        logger.info("Generated answer successfully.")
        return answer

    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        return f"Fout bij het genereren van antwoord: {str(e)}"

# Functie om een pre-query proces uit te voeren om de index voor te bereiden
def pre_indexing(content: str, chunk_size: int = 500):
    """
    Pre-index de tekst en maak deze klaar voor zoekopdrachten.
    Verdeel de tekst in chunks en bereken de embeddings.
    """
    # Splits de content in kleinere chunks (kan worden geoptimaliseerd voor grotere teksten)
    chunks = split_text_into_chunks(content, chunk_size)
    embeddings = model.encode(chunks)
    dimension = embeddings.shape[1]
    
    # Maak een FAISS-index en voeg de embeddings toe
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings, dtype=np.float32))

    logger.info(f"Index building completed with {len(chunks)} chunks.")
    return index, chunks

# Functie om de inhoud van een tekst in kleinere stukken (chunks) te splitsen
def split_text_into_chunks(text: str, chunk_size: int = 500) -> list:
    """
    Verdeel de tekst in kleinere stukken (chunks) van een opgegeven grootte.
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

