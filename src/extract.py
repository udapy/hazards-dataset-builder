import io
import trafilatura
from pypdf import PdfReader
import sqlite3
import pandas as pd
from .store import DB_NAME

def extract_from_html(content_bytes):
    """
    Extracts text from HTML content using trafilatura.
    """
    try:
        # trafilatura expects string for extract, but can handle bytes if we decode or use bare_extraction with bytes?
        # actually trafilatura.extract takes a string. 
        # But we can pass the bytes to trafilatura.utils.decode_file or just try decoding.
        # Safest is to let trafilatura handle it if possible, but extract() takes a string.
        # Let's try to decode first.
        
        # Simple decode attempt
        try:
             text_content = content_bytes.decode('utf-8')
        except UnicodeDecodeError:
             # Fallback to latin-1 or let trafilatura guess if we passed raw bytes to a different function
             # But for now let's assume utf-8 or latin-1
             text_content = content_bytes.decode('latin-1')

        extracted = trafilatura.extract(text_content)
        return extracted if extracted else ""
    except Exception as e:
        print(f"Error extracting HTML: {e}")
        return ""

def extract_from_pdf(content_bytes):
    """
    Extracts text from PDF bytes using pypdf.
    """
    try:
        pdf_file = io.BytesIO(content_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def extract_content(content_bytes, content_type):
    """
    Dispatches extraction based on content type.
    """
    if 'pdf' in content_type:
        return extract_from_pdf(content_bytes)
    elif 'html' in content_type:
        return extract_from_html(content_bytes)
    else:
        # Fallback to treating as text/html if unknown, or just try to decode
        print(f"Unknown content type: {content_type}, attempting HTML extraction.")
        return extract_from_html(content_bytes)
