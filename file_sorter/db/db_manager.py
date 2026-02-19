import sqlite3

DB_NAME = "documents.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            path TEXT UNIQUE,
            source TEXT,
            letter_type TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def insert_document(title, path, source, letter_type):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO documents (title, path, source, letter_type)
        VALUES (?, ?, ?, ?)
    """, (title, path, source, letter_type))

    conn.commit()
    conn.close()


def fetch_documents():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, path, source, letter_type, date_added
        FROM documents
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_document_by_id(doc_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT path FROM documents WHERE id = ?", (doc_id,))
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else None


def document_exists(path):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM documents WHERE path = ?", (path,))
    result = cursor.fetchone()

    conn.close()
    return result is not None


def get_categories():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT letter_type, COUNT(*) 
        FROM documents 
        GROUP BY letter_type
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_documents_by_category(category):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, path, source, letter_type, date_added
        FROM documents
        WHERE letter_type = ?
    """, (category,))

    rows = cursor.fetchall()
    conn.close()
    return rows

