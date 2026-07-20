import sqlite3

def setup_module_content_db():
    conn = sqlite3.connect("curriculum.db")
    cursor = conn.cursor()
    
    # 1. Create the structured data table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS modules_content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module_name TEXT NOT NULL,
        step_order INTEGER NOT NULL,
        title TEXT NOT NULL,
        instruction TEXT NOT NULL,
        task TEXT,
        initial_code TEXT,
        verify_keyword TEXT,
        show_sandbox BOOLEAN NOT NULL DEFAULT 0
    )
    """)
    
    # 2. Clear out any previous dummy items
    cursor.execute("DELETE FROM modules_content")
    
    # 3. Seed the unique phase blocks for our distinct modules
    content_data = [
        # --- CSS GRID LAYOUTS ---
        ("CSS Grid Layouts", 1, "1. Core Concepts of 2D Layouts", 
         "Unlike Flexbox (which is primarily one-dimensional), CSS Grid gives you absolute coordinate structural alignment over columns and rows simultaneously. It transforms containers into powerful blueprints without needing complex margin hacks.", 
         None, None, None, 0),
        ("CSS Grid Layouts", 2, "2. The Magic of auto-fill & minmax", 
         "Using rules like `grid-template-columns: repeat(auto-fill, minmax(200px, 1fr))` tells the browser to fit as many columns as possible, but never shrink them below 200px. This creates native responsiveness without a million manual media breakpoints.", 
         None, None, None, 0),
        ("CSS Grid Layouts", 3, "3. Coding Challenge", 
         "Ready to wire it up yourself? Apply what you've learned to build a fully automated card layout grid.", 
         "Inside the `.grid-canvas` wrapper class rules, declare `display: grid;` and implement a fluid dynamic column strategy using `repeat(auto-fill, minmax(200px, 1fr));`", 
         ".grid-canvas {\n  /* Implement responsive grid columns here */\n  gap: 16px;\n}", "auto-fill", 1),

        # --- ASYNCHRONOUS FETCH PROCESSING ---
        ("Asynchronous Fetch Processing", 1, "1. The Power of Async/Await", 
         "Modern web apps don't reload the entire page; they talk to APIs in the background. JavaScript handles this using Promises, and the modern way to write this is via the `async` and `await` keywords, making asynchronous code read like clean synchronous steps.", 
         None, None, None, 0),
        ("Asynchronous Fetch Processing", 2, "2. Trapping Errors Safely", 
         "When networks drop or backends crash with a 500 error, unhandled promises will break your frontend app framework execution. Wrapping network communications inside a standard try/catch block ensures your program handles faults gracefully.", 
         None, None, None, 0),
        ("Asynchronous Fetch Processing", 3, "3. Coding Challenge", 
         "Let's write a secure data pipeline wrapper function.", 
         "Complete the async handler execution block. Write an await fetch request pointing to '/api/course-details?id=1' and parse the JSON response cleanly.", 
         "async function fetchCourseData() {\n  try {\n    // Write your async fetch pipeline here\n    \n  } catch (error) {\n    console.error('Fetch failure trapped:', error);\n  }\n}", "fetch", 1),

        # --- CUSTOM HOOKS PATTERN ---
        ("Custom Hooks Pattern", 1, "1. Why Extract Component Logic?", 
         "In React, as components grow, mixing layout UI code with state logic engines (like fetch synchronization, event listeners, or complex timers) creates massive, unreadable files. Extracting that logic makes your systems modular.", 
         None, None, None, 0),
        ("Custom Hooks Pattern", 2, "2. Naming Conventions", 
         "React identifies custom state configurations by tracking functional extensions that start explicitly with the word 'use'. For example, `useSpaceData` or `useAuth`. This unlocks inside them the ability to invoke core hooks natively.", 
         None, None, None, 0),
        ("Custom Hooks Pattern", 3, "3. Coding Challenge", 
         "Isolate functional component operations cleanly.", 
         "Encapsulate structural telemetry data state hooks logic safely inside a custom hook wrapper named useSpaceData.", 
         "// Extract component engine logic here\nfunction useSpaceData() {\n  // Implement hooks wrapper\n}", "useSpaceData", 1)
    ]
    
    cursor.executemany("""
    INSERT INTO modules_content (module_name, step_order, title, instruction, task, initial_code, verify_keyword, show_sandbox)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, content_data)
    
    conn.commit()
    conn.close()
    print("🚀 Curriculum DB modules content table seeded successfully!")


setup_module_content_db()