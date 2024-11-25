import sqlite3
import chromadb
from chromadb.config import Settings

# Initialize SQLite database
def init_sqlite_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT,
            description TEXT,
            start_date TEXT,
            due_date TEXT,
            time_spent TEXT,
            functional_area TEXT,
            assignment TEXT,
            task_type TEXT,
            status INTEGER
        )
    """)
    conn.commit()
    return conn

# Initialize ChromaDB
def init_chromadb():
    client = chromadb.PersistentClient()
    collection = client.get_or_create_collection(name="tasks")
    return collection
