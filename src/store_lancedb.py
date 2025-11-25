import lancedb
import pyarrow as pa
import numpy as np
import json
import os

LANCEDB_URI = "data/lancedb_data"

def init_db():
    os.makedirs(LANCEDB_URI, exist_ok=True)
    db = lancedb.connect(LANCEDB_URI)
    
    # Define schema
    schema = pa.schema([
        pa.field("source_url", pa.string()),
        pa.field("content_type", pa.string()),
        pa.field("extracted_text", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), 384)), # Assuming 384 dim
        pa.field("metadata", pa.string()) # JSON string
    ])
    
    try:
        db.create_table("documents", schema=schema, exist_ok=True)
    except Exception as e:
        print(f"Table documents might already exist: {e}")

    # New Granular Schema
    structured_schema = pa.schema([
        pa.field("hazard_type", pa.string()),
        pa.field("phase", pa.string()),
        pa.field("audience", pa.string()),
        pa.field("topic", pa.string()),
        pa.field("content_raw", pa.string()),
        pa.field("action_items", pa.string()), # JSON string
        pa.field("sources", pa.string()), # JSON string
        pa.field("source_file", pa.string()),
        pa.field("page_ref", pa.int32()),
        pa.field("last_updated", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), 384))
    ])

    try:
        db.create_table("structured_hazards", schema=structured_schema, exist_ok=True)
    except Exception as e:
        print(f"Table structured_hazards might already exist: {e}")

def save_document(source_url, content_type, extracted_text, embedding, metadata):
    db = lancedb.connect(LANCEDB_URI)
    table_name = "documents"
    
    tbl = db.open_table(table_name)
    
    data = [{
        "source_url": source_url,
        "content_type": content_type,
        "extracted_text": extracted_text,
        "vector": embedding,
        "metadata": json.dumps(metadata)
    }]
    
    tbl.add(data)

def save_structured_document(data, embedding):
    db = lancedb.connect(LANCEDB_URI)
    
    if embedding is not None:
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
    
    # Ensure data matches schema
    record = {
        "hazard_type": data.get('hazard_type', ''),
        "phase": data.get('phase', 'Prepare'),
        "audience": data.get('audience', 'General'),
        "topic": data.get('topic', ''),
        "content_raw": data.get('content_raw', ''),
        "action_items": json.dumps(data.get('action_items', [])),
        "sources": json.dumps(data.get('sources', [])),
        "source_file": data.get('source_file', ''),
        "page_ref": int(data.get('page_ref', 0)),
        "last_updated": data.get('last_updated', ''),
        "vector": embedding
    }
    
    try:
        tbl = db.open_table("structured_hazards")
        tbl.add([record])
    except Exception as e:
        print(f"Error saving to LanceDB: {e}")
    tbl = db.open_table("documents")
    return tbl.to_pandas()

def get_all_documents():
    db = lancedb.connect(LANCEDB_URI)
    tbl = db.open_table("documents")
    return tbl.to_pandas()
