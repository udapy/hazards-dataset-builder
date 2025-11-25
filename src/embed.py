from sentence_transformers import SentenceTransformer
import numpy as np

# Global model instance to avoid reloading
_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def generate_embedding(text):
    """
    Generates an embedding for the given text.
    Returns a numpy array (or bytes).
    """
    if not text or not text.strip():
        return None
    
    model = get_model()
    embedding = model.encode(text)
    return embedding
