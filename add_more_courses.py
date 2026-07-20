# add_more_courses.py
import sqlite3

def add_courses():
    conn = sqlite3.connect("curriculum.db")
    cursor = conn.cursor()
    
    # 📚 1. Inject More High-Value Core Courses
    more_courses = [
        ("React & State Architecture", "Master hooks, custom state management tools, context APIs, and highly performant component lifecycles.", "Advanced"),
        ("Database Systems & Design", "Dive deep into relational query structures, indexing patterns, transactions, and performance optimizations.", "Advanced"),
        ("Version Control with Git", "Learn branching strategies, stash spaces, rebasing mechanics, and team workflow pipeline configurations.", "Beginner"),
        ("Data Wrangling with Pandas", "Clean, transform, manipulate, and analyze structured datasets using modern NumPy and Pandas matrices.", "Intermediate"),
        ("Machine Learning Foundations", "Implement mathematical regressions, decision vectors, classification limits, and unsupervised clusters.", "Intermediate"),
        ("Docker & Containerization", "Package web apps, construct optimized files, configure multi-container compositions, and ship environments.", "Advanced")
    ]
    
    cursor.executemany(
        "INSERT OR IGNORE INTO courses (title, description, difficulty) VALUES (?, ?, ?)",
        more_courses
    )
    conn.commit()
    
    # Grab the generated mapping keys
    cursor.execute("SELECT id, name FROM roles")
    role_ids = {row[1]: row[0] for row in cursor.fetchall()}
    
    cursor.execute("SELECT id, title FROM courses")
    course_ids = {row[1]: row[0] for row in cursor.fetchall()}
    
    # 🔗 2. Map the new items to the Frontend and Backend Roles
    new_relations = [
        # Frontend Additions
        (role_ids["Frontend Developer"], course_ids["React & State Architecture"]),
        (role_ids["Frontend Developer"], course_ids["Version Control with Git"]),
        
        # Backend Additions
        (role_ids["Backend Engineer"], course_ids["Database Systems & Design"]),
        (role_ids["Backend Engineer"], course_ids["Docker & Containerization"]),
        (role_ids["Backend Engineer"], course_ids["Version Control with Git"])
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO role_courses (role_id, course_id) VALUES (?, ?)", new_relations)
    
    # 🎯 3. Add Key Sub-Skills to these Courses
    more_skills = [
        (course_ids["React & State Architecture"], "Custom Hooks Pattern", "Extracting component logic into reusable structural hooks."),
        (course_ids["Database Systems & Design"], "Index Optimizations", "Accelerating query scanning metrics using precise column indexing."),
        (course_ids["Docker & Containerization"], "Multi-stage Builds", "Minimizing final application deployment container footprints.")
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO skills (course_id, name, description) VALUES (?, ?, ?)", more_skills)
    
    conn.commit()
    conn.close()
    print("📚 Catalog beautifully expanded with fresh, diverse technical tracks!")

if __name__ == "__main__":
    add_courses()