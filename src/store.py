import sqlite3
import json
import numpy as np
import os

DB_NAME = "data/hazards.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_url TEXT,
            content_type TEXT,
            extracted_text TEXT,
            embedding BLOB,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # New Granular Schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS structured_hazards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hazard_type TEXT,
            phase TEXT,
            audience TEXT,
            topic TEXT,
            content_raw TEXT,
            action_items TEXT,
            sources TEXT,
            source_file TEXT,
            page_ref INTEGER,
            last_updated DATE,
            embedding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_document(source_url, content_type, extracted_text, embedding, metadata):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Serialize embedding
    embedding_blob = np.array(embedding, dtype=np.float32).tobytes()
    
    cursor.execute('''
        INSERT INTO documents (source_url, content_type, extracted_text, embedding, metadata)
        VALUES (?, ?, ?, ?, ?)
    ''', (source_url, content_type, extracted_text, embedding_blob, json.dumps(metadata)))
    
    conn.commit()
    conn.close()

def save_structured_document(data, embedding):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Serialize embedding
    embedding_blob = None
    if embedding is not None:
        if isinstance(embedding, np.ndarray):
            embedding_blob = embedding.tobytes()
        else:
             # Assume list
             embedding_blob = np.array(embedding, dtype=np.float32).tobytes()

    cursor.execute('''
        INSERT INTO structured_hazards (
            hazard_type, phase, audience, topic, content_raw, 
            action_items, sources, source_file, page_ref, last_updated, embedding
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('hazard_type'),
        data.get('phase'),
        data.get('audience'),
        data.get('topic'),
        data.get('content_raw'),
        json.dumps(data.get('action_items', [])),
        json.dumps(data.get('sources', [])),
        data.get('source_file'),
        data.get('page_ref'),
        data.get('last_updated'),
        embedding_blob
    ))
    
    conn.commit()
    conn.close()

def get_all_documents():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM documents')
    rows = cursor.fetchall()
    conn.close()
    return rows
