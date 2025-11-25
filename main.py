import argparse
import sys
from src.scrape_hazards import scrape_hazards
from src.ingest_universal import ingest_universal
from src.process_pdfs import process_pdfs
from src.export import export_to_hf_dataset
from src.verify_data import verify_sqlite, verify_lancedb
from src.store import init_db as init_sqlite, save_document as save_sqlite
from src.store_lancedb import init_db as init_lancedb, save_document as save_lancedb

def process_url(url, use_lancedb=False):
    print(f"Processing {url}...")
    content, content_type = fetch_url(url)
    if not content:
        print(f"Failed to fetch {url}")
        return

    print(f"  Type: {content_type}")
    text = extract_content(content, content_type)
    if not text:
        print(f"  No text extracted from {url}")
        return
    
    print(f"  Extracted {len(text)} characters.")
    embedding = generate_embedding(text)
    
    metadata = {"original_url": url}
    
    if use_lancedb:
        save_lancedb(url, content_type, text, embedding, metadata)
        print(f"  Saved to LanceDB.")
    else:
        save_sqlite(url, content_type, text, embedding, metadata)
        print(f"  Saved to SQLite.")

def main():
    parser = argparse.ArgumentParser(description="Hazards Dataset Builder")
    parser.add_argument("--urls", nargs="+", help="List of URLs to process")
    parser.add_argument("--file", help="File containing URLs (one per line)")
    parser.add_argument("--export", action="store_true", help="Export DB to HF Dataset")
    parser.add_argument("--use-lancedb", action="store_true", help="Use LanceDB instead of SQLite")
    parser.add_argument("--push-to-hub", action="store_true", help="Push exported dataset to Hugging Face Hub")
    parser.add_argument("--repo-id", help="Hugging Face Repository ID (e.g. username/dataset)")
    parser.add_argument("--structured", action="store_true", help="Export structured dataset")
    
    parser.add_argument("--scrape", action="store_true", help="Scrape hazards")
    parser.add_argument("--ingest", action="store_true", help="Ingest universal data")
    parser.add_argument("--process", action="store_true", help="Process PDFs")
    parser.add_argument("--limit", type=int, help="Limit for scraper")
    
    args = parser.parse_args()

    if args.use_lancedb:
        init_lancedb()
    else:
        init_sqlite()

    if args.scrape:
        scrape_hazards(limit=args.limit)
        
    if args.ingest:
        ingest_universal()
        
    if args.process:
        process_pdfs(limit=args.limit)

    if args.urls:
        for url in args.urls:
            process_url(url, use_lancedb=args.use_lancedb)
            
    if args.file:
        try:
            with open(args.file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            for url in urls:
                process_url(url, use_lancedb=args.use_lancedb)
        except FileNotFoundError:
            print(f"File not found: {args.file}")

    if args.export:
        export_to_hf_dataset(
            use_lancedb=args.use_lancedb,
            push_to_hub=args.push_to_hub,
            repo_id=args.repo_id,
            structured=args.structured
        )

if __name__ == "__main__":
    main()
