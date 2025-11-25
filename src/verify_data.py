import sqlite3
import lancedb
import json
import pandas as pd
from .store import DB_NAME
from .store_lancedb import LANCEDB_URI

def verify_sqlite():
    print("\n--- Verifying SQLite ---")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables: {tables}")
    
    if "structured_hazards" in tables:
        cursor.execute("SELECT * FROM structured_hazards LIMIT 1")
        columns = [description[0] for description in cursor.description]
        print(f"Columns: {columns}")
        
        cursor.execute("SELECT COUNT(*) FROM structured_hazards")
        count = cursor.fetchone()[0]
        print(f"Records in 'structured_hazards': {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM structured_hazards LIMIT 1")
            row = cursor.fetchone()
            print("\nSample Record (SQLite):")
            for col, val in zip(columns, row):
                if col == "embedding" and val:
                    print(f"  {col}: <BLOB len={len(val)}>")
                elif col == "action_items":
                    print(f"  {col}: {val[:100]}...")
                elif col == "sources":
                    print(f"  {col}: {val[:100]}...")
                elif col == "content_raw":
                    print(f"  {col}: {val[:50]}...")
                else:
                    print(f"  {col}: {val}")
    conn.close()

def verify_lancedb():
    print("\n--- Verifying LanceDB ---")
    try:
        db = lancedb.connect(LANCEDB_URI)
        tables = db.table_names()
        print(f"Tables: {tables}")
        
        if "structured_hazards" in tables:
            tbl = db.open_table("structured_hazards")
            df = tbl.to_pandas()
            print(f"Records in 'structured_hazards': {len(df)}")
            
            if not df.empty:
                print("\nSample Record (LanceDB):")
                row = df.iloc[0]
                for col in df.columns:
                    val = row[col]
                    if col == "vector":
                        print(f"  {col}: <Vector len={len(val)}>")
                    elif col == "action_items":
                        print(f"  {col}: {str(val)[:100]}...")
                    elif col == "sources":
                        print(f"  {col}: {str(val)[:100]}...")
                    elif col == "content_raw":
                        print(f"  {col}: {str(val)[:50]}...")
                    else:
                        print(f"  {col}: {val}")
    except Exception as e:
        print(f"LanceDB Error: {e}")

if __name__ == "__main__":
    verify_sqlite()
    verify_lancedb()
