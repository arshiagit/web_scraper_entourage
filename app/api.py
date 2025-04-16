# app/api.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.scraper import scrape_website
from app.embeddings import build_faiss_index
from app.rag import retrieve_relevant_chunks, generate_answer

router = APIRouter()

# Request modellen
class URLRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    query: str

# Globale opslag
faiss_index = None
text_chunks = None
scraped_text = None

# Status opslag voor async indexering
processing_status = {
    "status": None,     # 'running', 'done', 'error'
    "details": None     # extra info of foutmelding
}

# === ASYNC INDEXERING ===
@router.post("/build_index_async", summary="Start async scraping en FAISS-indexering")
def build_index_async(request: URLRequest, background_tasks: BackgroundTasks):
    """
    Start het scraping/indexeren in de achtergrond om timeouts te vermijden.
    """
    processing_status["status"] = "running"
    processing_status["details"] = None
    background_tasks.add_task(_background_indexing_task, request.url)
    return {"message": "Indexering gestart in achtergrond. Check voortgang via /index_status."}

def _background_indexing_task(url: str):
    """
    Interne functie voor achtergrondverwerking van scraping + indexing.
    """
    global faiss_index, text_chunks, scraped_text
    try:
        content = scrape_website(url)
        if not content:
            raise Exception("Geen content gevonden tijdens scraping.")

        scraped_text = content
        faiss_index, text_chunks = build_faiss_index(content)

        processing_status["status"] = "done"
        processing_status["details"] = f"{len(text_chunks)} chunks geïndexeerd."
    except Exception as e:
        processing_status["status"] = "error"
        processing_status["details"] = str(e)

@router.get("/index_status", summary="Toon status van async scraping/indexering")
def index_status():
    """
    Check de status van een async indexing proces.
    """
    return processing_status
# === RAG QUERY ===
@router.post("/rag_query", summary="Voer een RAG-query uit")
def rag_query(request: QueryRequest):
    if faiss_index is None or text_chunks is None:
        raise HTTPException(status_code=400, detail="Index is niet opgebouwd. Voer eerst /build_index of /build_index_async uit.")
    try:
        relevant_chunks = retrieve_relevant_chunks(request.query, faiss_index, text_chunks, top_k=3)
        answer = generate_answer(request.query, relevant_chunks)
        context_text = "\n---\n".join(relevant_chunks)
        return {
            "query": request.query,
            "answer": answer,
            "num_chunks_used": len(relevant_chunks),
            "context_preview": context_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === DEBUG TOOLS ===
@router.get("/show_scraped_text", summary="Toon volledige gescrapete tekst")
def show_scraped_text():
    if scraped_text is None:
        raise HTTPException(status_code=404, detail="Nog geen tekst beschikbaar. Voer eerst /build_index of async versie uit.")
    return {
        "length": len(scraped_text),
        "preview": scraped_text[:1000] + ("..." if len(scraped_text) > 1000 else "")
    }

@router.get("/show_chunks", summary="Toon de eerste 5 gegenereerde tekst-chunks")
def show_chunks():
    if text_chunks is None:
        raise HTTPException(status_code=404, detail="Geen chunks beschikbaar. Voer eerst /build_index of async versie uit.")
    return {
        "num_chunks": len(text_chunks),
        "chunk_preview": text_chunks[:5]
    }
