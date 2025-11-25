import os
import shutil
from datasets import load_from_disk
from main import process_url, export_to_hf_dataset
from store_lancedb import init_db, get_all_documents

def test_lancedb_pipeline():
    # Setup
    if os.path.exists("data/lancedb"):
        shutil.rmtree("data/lancedb")
    if os.path.exists("hf_dataset_lancedb"):
        shutil.rmtree("hf_dataset_lancedb")
    
    init_db()
    
    # Test URL processing
    test_url = "https://www.example.com"
    print(f"Testing processing of {test_url} with LanceDB...")
    process_url(test_url, use_lancedb=True)
    
    # Verify LanceDB
    df = get_all_documents()
    print(f"LanceDB has {len(df)} records.")
    
    if len(df) == 1:
        print("SUCCESS: LanceDB has 1 record.")
    else:
        print(f"FAILURE: LanceDB has {len(df)} records.")
        return

    # Test Export
    print("Testing export to HF Dataset from LanceDB...")
    export_to_hf_dataset(output_path="hf_dataset_lancedb", use_lancedb=True)
    
    # Verify HF Dataset
    try:
        ds = load_from_disk("hf_dataset_lancedb")
        print(f"SUCCESS: Loaded HF Dataset with {len(ds)} records.")
        print("Sample record:", ds[0])
    except Exception as e:
        print(f"FAILURE: Could not load HF Dataset. {e}")

if __name__ == "__main__":
    test_lancedb_pipeline()
