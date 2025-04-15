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

# Globale variabelen om index, chunks en scraped text op te slaan
faiss_index = None
text_chunks = None
scraped_text = None  # Variabele om de volledige gescrapete tekst op te slaan

@router.post("/build_index", summary="Scrape website en bouw FAISS-index")
def build_index(request: URLRequest):
    """
    Scrape de website op basis van de URL, bereken embeddings en bouw een FAISS-index.
    """
    global faiss_index, text_chunks, scraped_text
    try:
        content = scrape_website(request.url)
        if not content:
            raise HTTPException(status_code=404, detail="Geen content gevonden op de website")
        scraped_text = content  # Bewaar de volledige tekst
        faiss_index, text_chunks = build_faiss_index(content)
        return {"status": "Index is succesvol gebouwd", "num_chunks": len(text_chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rag_query", summary="Voer een RAG-query uit")
def rag_query(request: QueryRequest):
    """
    Haal de meest relevante chunks op uit de index en genereer een antwoord via OpenAI.
    Geeft ook de samengevoegde context-tekst terug ter debug.
    """
    if faiss_index is None or text_chunks is None:
        raise HTTPException(status_code=400, detail="Index is niet opgebouwd. Voer eerst /build_index uit.")
    
    try:
        relevant_chunks = retrieve_relevant_chunks(request.query, faiss_index, text_chunks, top_k=3)
        answer = generate_answer(request.query, relevant_chunks)
        context_text = "\n---\n".join(relevant_chunks)  # Voeg de context samen om makkelijk te bekijken

        return {
            "query": request.query,
            "answer": answer,
            "num_chunks_used": len(relevant_chunks),
            "context_preview": context_text  # Dit toont de samengevoegde tekst
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/show_scraped_text", summary="Toon volledige gescrapete tekst")
def show_scraped_text():
    """
    Retourneert de volledige, ongesplitste gescrapete tekst als debug.
    """
    if scraped_text is None:
        raise HTTPException(status_code=404, detail="Nog geen tekst beschikbaar. Voer eerst /build_index uit.")
    return {
        "length": len(scraped_text),
        "preview": scraped_text[:1000] + ("..." if len(scraped_text) > 1000 else "")
    }

@router.get("/show_chunks", summary="Toon alle gegenereerde chunks/batches")
def show_chunks():
    """
    Retourneert de eerste 5 chunks van de tekst (voor debugging) en de totale hoeveelheid chunks.
    """
    if text_chunks is None:
        raise HTTPException(status_code=404, detail="Geen chunks beschikbaar. Voer eerst /build_index uit.")
    
    # Toon de eerste 5 chunks en een aantal andere details
    chunk_preview = text_chunks[:5]
    return {
        "num_chunks": len(text_chunks),
        "chunk_preview": chunk_preview
    }
