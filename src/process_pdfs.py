import os
import json
import re
import datetime
import pymupdf4llm
import pathlib
from .embed import generate_embedding
from .store import init_db as init_sqlite, save_structured_document as save_sqlite_struct
from .store_lancedb import init_db as init_lancedb, save_structured_document as save_lancedb_struct

# Ensure DBs are initialized
init_sqlite()
init_lancedb()

PDF_DIR = "data/raw"

def extract_metadata(text, hazard_name):
    """
    Extracts Phase, Audience, Topic, and Action Items from text chunk.
    """
    meta = {
        "phase": "Prepare", # Default
        "audience": "General",
        "topic": "General Safety",
        "action_items": []
    }
    
    text_lower = text.lower()
    
    # Phase Detection
    if any(kw in text_lower for kw in ['prepare', 'prevention', 'before', 'planning']):
        meta["phase"] = "Prepare"
    elif any(kw in text_lower for kw in ['react', 'response', 'during', 'action', 'emergency']):
        meta["phase"] = "React"
    elif any(kw in text_lower for kw in ['recover', 'after', 'restoration', 'cleanup']):
        meta["phase"] = "Recover"
        
    # Audience Detection
    if any(kw in text_lower for kw in ['kid', 'child', 'children', 'baby', 'infant']):
        meta["audience"] = "Kids"
    elif any(kw in text_lower for kw in ['elderly', 'senior', 'aged', 'older adult']):
        meta["audience"] = "Elderly"
    elif any(kw in text_lower for kw in ['farm', 'livestock', 'cattle', 'horse']):
        meta["audience"] = "Farm Animals"
    elif any(kw in text_lower for kw in ['pet', 'dog', 'cat', 'animal']):
        meta["audience"] = "Pets"
        
    # Topic Detection (First Header)
    # Filter out generic headers
    generic_headers = [
        "table of contents", "introduction", "overview", "references", "sources", 
        "conclusion", "summary", "appendix", "index", "glossary", "preface",
        "safety", "general", "disclaimer", "copyright", "acknowledgments",
        hazard_name.lower() # Avoid redundancy
    ]
    
    headers = re.findall(r'^#+\s+(.+)$', text, re.MULTILINE)
    for header in headers:
        header_clean = header.strip()
        if header_clean.lower() not in generic_headers:
            # Also check if it's too short or looks like a page number
            if len(header_clean) > 3 and not header_clean.isdigit():
                meta["topic"] = header_clean
                break
        
    # Action Items Extraction
    # Look for lines starting with -, *, or numbers like 1.
    action_items = []
    for line in text.split('\n'):
        line = line.strip()
        if re.match(r'^[-*]\s+', line) or re.match(r'^\d+\.\s+', line):
            # Clean the item
            item = re.sub(r'^[-*]\s+', '', line)
            item = re.sub(r'^\d+\.\s+', '', item)
            if len(item) > 5: # Filter noise
                action_items.append(item)
    meta["action_items"] = action_items
    
    # Sources Extraction
    # Look for Markdown links [Title](URL) and plain URLs
    sources = []
    
    # Markdown links
    md_links = re.findall(r'\[([^\]]+)\]\((http[s]?://[^)]+)\)', text)
    for title, url in md_links:
        sources.append({"title": title, "url": url})
        
    # Plain URLs (avoid duplicates if already caught by markdown regex)
    # This simple regex might catch URLs inside markdown links again, so we filter
    plain_urls = re.findall(r'(?<!\()(http[s]?://[^\s\)]+)', text)
    existing_urls = {s["url"] for s in sources}
    
    for url in plain_urls:
        if url not in existing_urls:
            # Use domain or truncated URL as title
            title = url.split('//')[-1].split('/')[0]
            sources.append({"title": title, "url": url})
            existing_urls.add(url)
            
    meta["sources"] = sources
    
    return meta

def process_pdfs(limit=None):
    if not os.path.exists(PDF_DIR):
        print(f"Directory not found: {PDF_DIR}")
        return

    files = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]
    total_files = len(files)
    print(f"Found {total_files} PDFs.")
    
    count = 0
    for i, f in enumerate(files):
        if limit and count >= limit:
            break
            
        pdf_path = os.path.join(PDF_DIR, f)
        print(f"[{i+1}/{total_files}] Processing {f}...")
        
        try:
            # Get last updated date from file
            fname = pathlib.Path(pdf_path)
            mtime = datetime.datetime.fromtimestamp(fname.stat().st_mtime)
            last_updated = mtime.strftime("%Y-%m-%d")
            
            # Convert PDF to Markdown pages
            # page_chunks=True returns a list of dictionaries
            pages = pymupdf4llm.to_markdown(pdf_path, page_chunks=True)
            
            hazard_type = f.replace(".pdf", "").replace("_", " ").replace("-", " ").title()
            
            current_topic = "General Safety"
            
            for page in pages:
                text = page['text']
                page_num = page['metadata']['page']
                
                # Extract metadata
                meta = extract_metadata(text, hazard_type)
                
                # Update topic if found, else keep previous
                if meta["topic"] != "General Safety":
                    current_topic = meta["topic"]
                else:
                    meta["topic"] = current_topic
                
                # Prepare data record
                record = {
                    "hazard_type": hazard_type,
                    "phase": meta["phase"],
                    "audience": meta["audience"],
                    "topic": meta["topic"],
                    "content_raw": text,
                    "action_items": meta["action_items"],
                    "sources": meta.get("sources", []),
                    "source_file": f,
                    "page_ref": page_num,
                    "last_updated": last_updated
                }
                
                # Generate embedding for the chunk
                # Combine important fields for semantic search
                embed_text = f"{hazard_type} {meta['phase']} {meta['topic']} {text}"
                embedding = generate_embedding(embed_text)
                
                # Save to DBs
                save_sqlite_struct(record, embedding)
                save_lancedb_struct(record, embedding)
            
            count += 1
            
        except Exception as e:
            print(f"Error processing {f}: {e}")
            continue
        
    print("Finished processing PDFs.")

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process PDFs")
    parser.add_argument("--limit", type=int, help="Limit number of PDFs to process")
    args = parser.parse_args()
    process_pdfs(limit=args.limit)
