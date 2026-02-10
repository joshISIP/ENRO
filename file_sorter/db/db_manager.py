import sqlite3
import os
from datetime import datetime

DB_NAME = "documents.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        file_path TEXT NOT NULL,
        source TEXT,
        date_added TEXT
        )
        """
    )

    conn.commit()
    conn.close()

def insert_document(title, file_path, source,):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO documents (title, file_path, source, date_added)
        VALUES (?, ?, ?, ?)
        """, (title, file_path, source, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    conn.commit()
    conn.close()

def fetch_documents():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM documents")
    rows = cursor.fetchall()

    conn.close()
    return rows



def get_document_by_id(doc_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT file_path FROM documents WHERE id = ?",
        (doc_id,)
    )

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None









def document_exists(file_path):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM documents WHERE file_path = ?",
        (file_path,)
    )

    exists = cursor.fetchone() is not None
    conn.close()
    return exists
