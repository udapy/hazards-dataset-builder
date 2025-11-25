import requests
from bs4 import BeautifulSoup
from .embed import generate_embedding
from .store import save_document, init_db

# Initialize DB
init_db()

def fetch_url(url):
    """
    Fetches the content of a URL.
    Returns a tuple (content_bytes, content_type).
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '').split(';')[0].strip()
        if not content_type:
             # Try to guess from URL
             guessed_type, _ = mimetypes.guess_type(url)
             if guessed_type:
                 content_type = guessed_type
             else:
                 content_type = 'text/html' # Default to HTML
                 
        return response.content, content_type
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None, None
