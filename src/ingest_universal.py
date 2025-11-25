import argparse
import os
import requests
import re
from urllib.parse import urljoin, urlparse
import time
from bs4 import BeautifulSoup
import trafilatura
from pypdf import PdfReader
from .embed import generate_embedding
from .store import init_db, save_document
from .store_lancedb import init_db as init_lancedb, save_document as save_lancedb

# Ensure DBs are initialized
init_db()
init_lancedb()

DATA_DIR = "data/universal_downloads"
os.makedirs(DATA_DIR, exist_ok=True)

def download_file(url, dest_folder):
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        filename = os.path.basename(urlparse(url).path)
        if not filename:
            filename = "downloaded_file.pdf" # Fallback
            
        filepath = os.path.join(dest_folder, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return filepath
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

def structure_text(text):
    """
    Heuristically structures text into Prepare, React, Recover sections.
    """
    sections = {
        "Prepare": "",
        "React": "",
        "Recover": "",
        "General": ""
    }
    
    # Simple keyword-based splitting
    # We look for headers or strong signals. 
    # This is a naive implementation.
    
    lines = text.split('\n')
    current_section = "General"
    
    prepare_keywords = ["prepare", "prevention", "before", "planning"]
    react_keywords = ["react", "response", "during", "action", "emergency"]
    recover_keywords = ["recover", "after", "restoration", "cleanup"]
    
    for line in lines:
        lower_line = line.lower().strip()
        
        # Check if line looks like a header (short, no punctuation at end usually)
        if len(lower_line) < 50:
            if any(k in lower_line for k in prepare_keywords):
                current_section = "Prepare"
            elif any(k in lower_line for k in react_keywords):
                current_section = "React"
            elif any(k in lower_line for k in recover_keywords):
                current_section = "Recover"
        
        sections[current_section] += line + "\n"
        
    # Format for storage
    formatted_text = ""
    for sec, content in sections.items():
        if content.strip():
            formatted_text += f"\n\n--- SECTION: {sec} ---\n\n{content.strip()}"
            
    return formatted_text

def ingest_universal(input_path=None):
    if not input_path:
        print("No input path provided for ingestion.")
        return

    print(f"Processing {input_path}...")
    
    extracted_text = ""
    content_type = ""
    metadata = {"original_source": input_path, "attachments": []}
    
    if input_path.startswith("http"):
        # URL Processing
        try:
            response = requests.get(input_path, timeout=10)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            
            if 'pdf' in content_type:
                # It's a PDF URL
                pdf_path = download_file(input_path, DATA_DIR)
                if pdf_path:
                    extracted_text = extract_text_from_pdf(pdf_path)
                    metadata["local_path"] = pdf_path
            else:
                # It's likely HTML
                extracted_text = trafilatura.extract(response.text)
                
                # Look for PDF links
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.lower().endswith('.pdf'):
                        abs_url = urljoin(input_path, href)
                        print(f"Found attachment: {abs_url}")
                        att_path = download_file(abs_url, DATA_DIR)
                        if att_path:
                            metadata["attachments"].append(att_path)
                            
        except Exception as e:
            print(f"Error fetching URL: {e}")
            return

    else:
        # Local File Processing
        if not os.path.exists(input_path):
            print(f"File not found: {input_path}")
            return
            
        if input_path.lower().endswith('.pdf'):
            content_type = "application/pdf"
            extracted_text = extract_text_from_pdf(input_path)
        else:
            # Assume text or html file
            content_type = "text/plain"
            with open(input_path, 'r', errors='ignore') as f:
                extracted_text = f.read()

    if not extracted_text:
        print("No text extracted.")
        return

    # Structure the text
    structured_text = structure_text(extracted_text)
    
    # Generate Embedding
    embedding = generate_embedding(structured_text)
    
    # Save to DBs
    save_sqlite(input_path, content_type, structured_text, embedding, metadata)
    save_lancedb(input_path, content_type, structured_text, embedding, metadata)
    
    print("Saved to SQLite and LanceDB.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Ingestion Script")
    parser.add_argument("--input", required=True, help="URL or file path to ingest")
    args = parser.parse_args()
    
    ingest_universal(args.input)
