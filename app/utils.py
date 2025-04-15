# app/utils.py
def split_text_into_chunks(text: str, chunk_size: int = 500) -> list:
    """
    Splitst de tekst in kleine stukken (chunks) van een opgegeven grootte.
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
