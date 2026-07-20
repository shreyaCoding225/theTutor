import sqlite3

# def init_database():
#     conn = sqlite3.connect("curriculum.db")
#     cursor = conn.cursor()

#     cursor.execute("PRAGMA foreign_keys = ON;")  #PRAGMA to enforce switches in sqlite

#     # roles/tracks table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS roles(
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL UNIQUE,
#             description TEXT
#         );
#     """)

#     #courses table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS courses (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             title TEXT NOT NULL UNIQUE,
#             description TEXT,
#             difficulty TEXT
#         );
#     """)

#     # role-courses mapping table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS role_courses (
#             role_id INTEGER,
#             course_id INTEGER,
#             PRIMARY KEY (role_id, course_id),
#             FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
#             FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
#         );
#     """)

#     # skills table (connected to parent course)
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS skills (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             course_id INTEGER,
#             name TEXT NOT NULL,
#             description TEXT,
#             FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
#         );
#     """)


#     # --- POPULATE SEED DATA ---
    
#     # Insert Roles
#     cursor.executemany(
#         "INSERT OR IGNORE INTO roles (name, description) VALUES (?, ?)",
#         [
#             ("Frontend Developer", "Builds modern responsive user interfaces and interactive web apps."),
#             ("Backend Engineer", "Designs scalable server application layers, secure APIs, and database models.")
#         ]
#     )
    
#     # Insert Courses
#     cursor.executemany(
#         "INSERT OR IGNORE INTO courses (title, description, difficulty) VALUES (?, ?, ?)",
#         [
#             ("HTML5 & CSS3 Essentials", "Learn layouts via Flexbox, CSS Grid, and responsive web principles.", "Beginner"),
#             ("Advanced JavaScript Hooks", "Master asynchronous execution pipelines, scoping structures, and modern DOM methods.", "Intermediate"),
#             ("FastAPI Fundamentals", "Learn Python API development, asynchronous routing, and auto-generated data models.", "Intermediate")
#         ]
#     )
    
#     conn.commit()
    
#     # Grab IDs to map connections correctly
#     cursor.execute("SELECT id, name FROM roles")
#     role_ids = {row[1]: row[0] for row in cursor.fetchall()}
    
#     cursor.execute("SELECT id, title FROM courses")
#     course_ids = {row[1]: row[0] for row in cursor.fetchall()}
    
#     # Map Courses to Roles
#     relations = [
#         (role_ids["Frontend Developer"], course_ids["HTML5 & CSS3 Essentials"]),
#         (role_ids["Frontend Developer"], course_ids["Advanced JavaScript Hooks"]),
#         (role_ids["Backend Engineer"], course_ids["FastAPI Fundamentals"])
#     ]
#     cursor.executemany("INSERT OR IGNORE INTO role_courses (role_id, course_id) VALUES (?, ?)", relations)
    
#     # Add Skills to Courses
#     skills = [
#         (course_ids["HTML5 & CSS3 Essentials"], "CSS Grid Layouts", "Positioning interfaces using two-dimensional row/column layouts."),
#         (course_ids["HTML5 & CSS3 Essentials"], "Responsive Media Queries", "Styling websites to shift layout dynamically across dimensions."),
#         (course_ids["Advanced JavaScript Hooks"], "Asynchronous Fetch Processing", "Communicating securely with web servers via Promises and Async/Await wrappers.")
#     ]
#     cursor.executemany("INSERT OR IGNORE INTO skills (course_id, name, description) VALUES (?, ?, ?)", skills)
    
#     conn.commit()
#     conn.close()
#     print("curriculum.db generated and populated with role-skill structures completely!")

# if __name__ == "__main__":
#     init_database()



# # to store progress
# def init_progress_table():
#     conn = sqlite3.connect('curriculum.db')
#     cursor = conn.cursor()
    
#     # Create the user_progress table
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS user_progress (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id TEXT NOT NULL,           -- To distinguish users later if needed
#             module_id TEXT NOT NULL,         -- Matches the 'module' URL parameter
#             step_index INTEGER NOT NULL,     -- Tracks how far they got, or final step
#             status TEXT DEFAULT 'completed', -- 'in_progress' or 'completed'
#             completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             UNIQUE(user_id, module_id)       -- Prevents duplicate completion entries
#         )
#     ''')
    
#     conn.commit()
#     conn.close()

# if __name__ == '__main__':
#     init_progress_table()

