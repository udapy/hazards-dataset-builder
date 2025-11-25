import os
import sqlite3
import shutil
from datasets import load_from_disk
from main import process_url, export_to_hf_dataset
from store import init_db

def test_pipeline():
    # Setup
    if os.path.exists("hazards.db"):
        os.remove("hazards.db")
    if os.path.exists("hf_dataset"):
        shutil.rmtree("hf_dataset")
    
    init_db()
    
    # Test URL processing
    test_url = "https://www.example.com"
    print(f"Testing processing of {test_url}...")
    process_url(test_url)
    
    # Verify SQLite
    conn = sqlite3.connect("hazards.db")
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM documents")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 1:
        print("SUCCESS: SQLite DB has 1 record.")
    else:
        print(f"FAILURE: SQLite DB has {count} records.")
        return

    # Test Export
    print("Testing export to HF Dataset...")
    export_to_hf_dataset()
    
    # Verify HF Dataset
    try:
        ds = load_from_disk("hf_dataset")
        print(f"SUCCESS: Loaded HF Dataset with {len(ds)} records.")
        print("Sample record:", ds[0])
    except Exception as e:
        print(f"FAILURE: Could not load HF Dataset. {e}")

if __name__ == "__main__":
    test_pipeline()
