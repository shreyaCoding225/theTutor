import sqlite3
from security import hash_password

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




# google btn

def verify_or_create_google_user(email: str, name: str) -> int:
    conn = sqlite3.connect("theTutor.db")
    cursor = conn.cursor()
    
    try:
        # 1. Check if the user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if user:
            return user[0]  # Return existing user ID
            
        # 2. Clean Insertion: No password field needed at all!
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )
        conn.commit()
        return cursor.lastrowid
        
    finally:
        conn.close()