# Web Scraper & RAG API

A Python-based web scraping and Retrieval-Augmented Generation (RAG) API built with FastAPI. This project combines web scraping capabilities with OpenAI's language models to provide intelligent responses based on scraped content.

## Features

- Web scraping functionality using BeautifulSoup4
- FastAPI backend with CORS support
- Integration with OpenAI's API for RAG capabilities
- FAISS-based vector storage for efficient similarity search
- Frontend integration support

## Prerequisites

- Python 3.8+
- OpenAI API key
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd web_scraper_entourage
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Project Structure

```
web_scraper_entourage/
├── app/                # Main application package
├── frontend/          # Frontend application
├── venv/              # Virtual environment
├── main.py            # Application entry point
├── requirements.txt   # Project dependencies
└── .env              # Environment variables
```

## Usage

1. Start the backend server:
```bash
python main.py
```

2. The API will be available at `http://localhost:8000`

3. Access the API documentation at `http://localhost:8000/docs`
