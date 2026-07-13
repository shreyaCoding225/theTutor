# migrate.py
import sqlite3

conn = sqlite3.connect("theTutor.db")
cursor = conn.cursor()

print("🚀 Starting database migration...")

# 1. Rename the old table to back it up safely
cursor.execute("ALTER TABLE users RENAME TO users_old;")

# 2. Create the new table where hashed_password is NOT strict (allows NULL)
cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        hashed_password TEXT NULL  -- 💡 Set to NULL so Google users can skip it!
    );
""")

# 3. Copy your existing user data from the old table to the new one
cursor.execute("""
    INSERT INTO users (id, name, email, hashed_password)
    SELECT id, name, email, hashed_password FROM users_old;
""")

# 4. Drop the old backup table
cursor.execute("DROP TABLE users_old;")

conn.commit()
conn.close()
print("🎉 Migration successful! The hashed_password column is now optional.")