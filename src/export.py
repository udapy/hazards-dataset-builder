import sqlite3
import pandas as pd
import json
import os
import lancedb
from datasets import Dataset, DatasetDict
from huggingface_hub import HfApi
import numpy as np

from .store import DB_NAME
from .store_lancedb import LANCEDB_URI
def export_to_hf_dataset(output_path="hf_dataset", use_lancedb=False, push_to_hub=False, repo_id=None, structured=False):
    if use_lancedb:
        print("Exporting from LanceDB...")
        table_name = "structured_hazards" if structured else "documents"
        try:
            db = lancedb.connect(LANCEDB_URI)
            tbl = db.open_table(table_name)
            df = tbl.to_pandas()
        except Exception as e:
            print(f"Error reading from LanceDB table {table_name}: {e}")
            return

        # LanceDB returns pandas df with vector as numpy array usually
        # We might need to ensure metadata/json fields are dicts if they are strings
        json_fields = ['metadata', 'hazard_prepare', 'hazard_react', 'hazard_recover', 'hazard_filters', 'hazard_sources']
        for field in json_fields:
            if field in df.columns:
                 df[field] = df[field].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
             
        # Rename vector to embedding to match previous schema if needed, or keep as vector
        if 'vector' in df.columns:
            df = df.rename(columns={'vector': 'embedding'})
            
    else:
        print("Exporting from SQLite...")
        conn = sqlite3.connect(DB_NAME)
        table_name = "structured_hazards" if structured else "documents"
        query = f"SELECT * FROM {table_name}"
        try:
            df = pd.read_sql_query(query, conn)
        except Exception as e:
             print(f"Error reading from SQLite table {table_name}: {e}")
             conn.close()
             return
        conn.close()
        
        # Convert embedding blob back to list for HF dataset
        def blob_to_list(blob):
            if blob:
                return np.frombuffer(blob, dtype=np.float32).tolist() # Assuming float32 from sentence-transformers
            return None

        if 'embedding' in df.columns:
            df['embedding'] = df['embedding'].apply(blob_to_list)
        
        # Convert JSON strings to dicts
        json_fields = ['metadata', 'hazard_prepare', 'hazard_react', 'hazard_recover', 'hazard_filters', 'hazard_sources']
        for field in json_fields:
            if field in df.columns:
                df[field] = df[field].apply(lambda x: json.loads(x) if x else {})

    if df.empty:
        print("No data to export.")
        return

    ds = Dataset.from_pandas(df)
    ds.save_to_disk(output_path)
    print(f"Dataset saved to {output_path}")
    
    if push_to_hub:
        if not repo_id:
            print("Error: --repo-id is required when pushing to Hub.")
            return ds
        
        print(f"Pushing to Hugging Face Hub: {repo_id}...")
        try:
            ds.push_to_hub(repo_id)
            print("Successfully pushed to Hub.")
        except Exception as e:
            print(f"Error pushing to Hub: {e}")
            
    return ds
