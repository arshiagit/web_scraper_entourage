# app/api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.scraper import scrape_website
from app.embeddings import build_faiss_index
from app.rag import retrieve_relevant_chunks, generate_answer

router = APIRouter()

class URLRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    query: str

# Globale variabelen om index en chunks op te slaan (in productie kan je dit opslaan in een database of cache)
faiss_index = None
text_chunks = None

@router.post("/build_index", summary="Scrape website en bouw FAISS-index")
def build_index(request: URLRequest):
    """
    Scrape de website op basis van de URL, bereken embeddings en bouw een FAISS-index.
    """
    global faiss_index, text_chunks
    try:
        content = scrape_website(request.url)
        if not content:
            raise HTTPException(status_code=404, detail="Geen content gevonden op de website")
        faiss_index, text_chunks = build_faiss_index(content)
        return {"status": "Index is succesvol gebouwd", "num_chunks": len(text_chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rag_query", summary="Voer een RAG-query uit")
def rag_query(request: QueryRequest):
    """
    Haal de meest relevante chunks op uit de index en genereer een antwoord via OpenAI.
    Zorg dat je eerst /build_index hebt aangeroepen.
    """
    if faiss_index is None or text_chunks is None:
        raise HTTPException(status_code=400, detail="Index is niet opgebouwd. Voer eerst /build_index uit.")
    
    try:
        relevant_chunks = retrieve_relevant_chunks(request.query, faiss_index, text_chunks, top_k=3)
        answer = generate_answer(request.query, relevant_chunks)
        return {"query": request.query, "answer": answer, "context": relevant_chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
