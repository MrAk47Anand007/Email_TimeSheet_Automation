import sqlite3



def init_sqlite_db():
    db_file = "tasks.db"  # Database file name
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create tasks table if not exists
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

    # Create task_versions table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_versions (
            version_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL REFERENCES tasks,
            task_name TEXT NOT NULL,
            version_date TEXT NOT NULL,
            version_data TEXT NOT NULL
        )
    """)

    conn.commit()
    print("SQLite database initialized and tables created.")
    return conn

