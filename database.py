import sqlite3
DB_NAME = "theTutor.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   email TEXT UNIQUE NOT NULL,
                   hashed_password TEXT NOT NULL
                   )
    ''')
    conn.commit()
    conn.close()