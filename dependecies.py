# check_dependencies.py
import sys
import pkg_resources
import platform
import os

def check_dependencies():
    """Check en print informatie over Python, OS en geïnstalleerde packages"""
    
    print("\n=== SYSTEEM INFORMATIE ===")
    print(f"Python versie: {sys.version}")
    print(f"OS: {platform.platform()}")
    
    print("\n=== OMGEVINGSVARIABELEN ===")
    # Veilig printen van env vars zonder gevoelige data te tonen
    for key in os.environ:
        if key.upper().find("KEY") >= 0 or key.upper().find("SECRET") >= 0 or key.upper().find("TOKEN") >= 0:
            value = os.environ[key]
            print(f"{key}: {'*' * len(value)}")
        else:
            print(f"{key}: {os.environ.get(key)}")
    
    print("\n=== GEÏNSTALLEERDE PACKAGES ===")
    installed_packages = [f"{dist.project_name}=={dist.version}" 
                         for dist in pkg_resources.working_set]
    installed_packages.sort()
    for package in installed_packages:
        print(package)
    
    print("\n=== OPENAI SPECIFIEKE INFO ===")
    try:
        import openai
        print(f"OpenAI Package versie: {openai.__version__}")
        print(f"OpenAI Package locatie: {openai.__file__}")
        
        try:
            from openai import OpenAI
            client = OpenAI()
            print("OpenAI client aangemaakt zonder errors")
        except Exception as e:
            print(f"Fout bij aanmaken OpenAI client: {str(e)}")
            
    except ImportError:
        print("OpenAI package is niet geïnstalleerd")
    
    print("\n=== FAISS INFO ===")
    try:
        import faiss
        print(f"FAISS geïnstalleerd")
    except ImportError:
        print("FAISS is niet geïnstalleerd")
    
    print("\n=== SENTENCE TRANSFORMERS INFO ===")
    try:
        import sentence_transformers
        print(f"Sentence-Transformers versie: {sentence_transformers.__version__}")
    except ImportError:
        print("Sentence-Transformers is niet geïnstalleerd")
        
    print("\n=== FASTAPI INFO ===")
    try:
        import fastapi
        print(f"FastAPI versie: {fastapi.__version__}")
    except ImportError:
        print("FastAPI is niet geïnstalleerd")

if __name__ == "__main__":
    check_dependencies()