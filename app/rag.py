# app/rag.py
import numpy as np
from app.embeddings import get_query_embedding
import faiss
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def retrieve_relevant_chunks(query: str, index: faiss.IndexFlatL2, chunks: list, top_k: int = 3) -> list:
    query_embedding = get_query_embedding(query)
    D, I = index.search(np.array([query_embedding], dtype=np.float32), top_k)
    relevant_chunks = [chunks[i] for i in I[0] if i < len(chunks)]
    return relevant_chunks

def generate_answer(query: str, context_chunks: list, max_tokens: int = 150) -> str:
    context = "\n---\n".join(context_chunks)
    prompt = (
        f"Gegeven de volgende context:\n{context}\n\n"
        f"Beantwoord de volgende vraag:\n{query}\n\n"
        "Antwoord in het Nederlands."
    )

    print("===> Sending request to OpenAI...")
    
    try:
        # Correcte API aanroep voor nieuwere OpenAI client versies
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Je bent een behulpzame assistent."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        print("===> Response received")
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"===> OpenAI call failed: {str(e)}")
        raise e